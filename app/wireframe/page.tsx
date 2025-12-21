'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store/authStore';
import { useDailyPlan, useCreateDailyPlan, useUpdateDailyPlan } from '@/lib/hooks/useDailyPlan';
import { useStartTimer, useUpdateTimer } from '@/lib/hooks/useTimer';
import { useDailyStats } from '@/lib/hooks/useStats';
import { useAutoSave } from '@/lib/hooks/useAutoSave';
import { TimeBlock as TimeBlockType } from '@/lib/api/client';

export default function WireframePage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();

  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedTime, setSelectedTime] = useState(50);
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [soundEnabled, setSoundEnabled] = useState(false);
  const [activeTimerId, setActiveTimerId] = useState<number | null>(null);

  // Local state for form inputs
  const [priorities, setPriorities] = useState(['', '', '']);
  const [brainDump, setBrainDump] = useState('');
  const [timeBlocks, setTimeBlocks] = useState<{ [key: string]: string }>({});

  const audioContextRef = useRef<AudioContext | null>(null);

  // Get date in YYYY-MM-DD format
  const dateString = currentDate.toISOString().split('T')[0];

  // Fetch daily plan
  const { data: dailyPlan, isLoading: isPlanLoading } = useDailyPlan(dateString);
  const createPlan = useCreateDailyPlan();
  const updatePlan = useUpdateDailyPlan();

  // Fetch daily stats
  const { data: stats } = useDailyStats(dateString);

  // Timer mutations
  const startTimerMutation = useStartTimer();
  const updateTimerMutation = useUpdateTimer();

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  // Load daily plan data into local state
  useEffect(() => {
    if (dailyPlan) {
      setPriorities(dailyPlan.priorities || ['', '', '']);
      setBrainDump(dailyPlan.brain_dump || '');

      // Convert time blocks array to object
      const blocksObj: { [key: string]: string } = {};
      dailyPlan.time_blocks?.forEach((block) => {
        const key = `${block.period}-${block.hour}`;
        blocksObj[key] = block.title || '';
      });
      setTimeBlocks(blocksObj);
    }
  }, [dailyPlan]);

  // Auto-save functionality
  const autoSaveData = {
    priorities,
    brainDump,
    timeBlocks,
  };

  useAutoSave({
    data: autoSaveData,
    onSave: async (data) => {
      if (!dailyPlan) {
        // Create new plan
        await createPlan.mutateAsync({
          date: dateString,
          priorities: data.priorities.filter(p => p.trim() !== ''),
          brain_dump: data.brainDump,
        });
      } else {
        // Update existing plan
        const timeBlocksArray: Partial<TimeBlockType>[] = [];

        // AM blocks
        for (let hour = 4; hour <= 12; hour++) {
          const key = `am-${hour}`;
          if (data.timeBlocks[key]) {
            timeBlocksArray.push({
              period: 'am' as const,
              hour,
              title: data.timeBlocks[key],
              planned_duration: 60, // Default 1 hour
            });
          }
        }

        // PM blocks
        for (let hour = 1; hour <= 12; hour++) {
          const key = `pm-${hour}`;
          if (data.timeBlocks[key]) {
            timeBlocksArray.push({
              period: 'pm' as const,
              hour,
              title: data.timeBlocks[key],
              planned_duration: 60,
            });
          }
        }

        await updatePlan.mutateAsync({
          id: dailyPlan.id,
          data: {
            priorities: data.priorities.filter(p => p.trim() !== ''),
            brain_dump: data.brainDump,
            time_blocks: timeBlocksArray,
          },
        });
      }
    },
    delay: 1500,
    enabled: isAuthenticated,
  });

  // Timer logic
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isTimerRunning && elapsedTime < selectedTime * 60) {
      interval = setInterval(() => {
        setElapsedTime((prev) => prev + 1);

        // Update timer in backend every 5 seconds
        if (activeTimerId && elapsedTime % 5 === 0) {
          updateTimerMutation.mutate({
            id: activeTimerId,
            data: { elapsed_time: elapsedTime },
          });
        }
      }, 1000);
    } else if (elapsedTime >= selectedTime * 60 && isTimerRunning) {
      setIsTimerRunning(false);
      handleTimerComplete();
    }
    return () => clearInterval(interval);
  }, [isTimerRunning, elapsedTime, selectedTime, activeTimerId]);

  // Timer complete handler
  const handleTimerComplete = async () => {
    if (soundEnabled) {
      playBeepSound();
    }

    // Complete timer session in backend
    if (activeTimerId) {
      await updateTimerMutation.mutateAsync({
        id: activeTimerId,
        data: {
          elapsed_time: selectedTime * 60,
          status: 'completed',
        },
      });
      setActiveTimerId(null);
    }
  };

  // Play beep sound
  const playBeepSound = () => {
    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
    }

    const ctx = audioContextRef.current;
    const now = ctx.currentTime;

    [0, 0.15, 0.3].forEach((offset) => {
      const oscillator = ctx.createOscillator();
      const gainNode = ctx.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(ctx.destination);

      oscillator.frequency.value = 800;
      oscillator.type = 'square';

      gainNode.gain.setValueAtTime(0.3, now + offset);
      gainNode.gain.exponentialRampToValueAtTime(0.01, now + offset + 0.1);

      oscillator.start(now + offset);
      oscillator.stop(now + offset + 0.1);
    });
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleStartTimer = async () => {
    if (!isTimerRunning) {
      setIsTimerRunning(true);

      // Create timer session in backend
      if (isAuthenticated) {
        const session = await startTimerMutation.mutateAsync({
          scheduled_duration: selectedTime * 60,
        });
        setActiveTimerId(session.id);
      }
    } else {
      setIsTimerRunning(false);

      // Pause timer in backend
      if (activeTimerId) {
        await updateTimerMutation.mutateAsync({
          id: activeTimerId,
          data: {
            elapsed_time: elapsedTime,
            status: 'paused',
          },
        });
      }
    }
  };

  const handleResetTimer = async () => {
    setIsTimerRunning(false);
    setElapsedTime(0);

    // Cancel timer in backend
    if (activeTimerId) {
      await updateTimerMutation.mutateAsync({
        id: activeTimerId,
        data: {
          status: 'cancelled',
        },
      });
      setActiveTimerId(null);
    }
  };

  const handleLogout = async () => {
    const { clearUser } = useAuthStore.getState();
    clearUser();
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    router.push('/login');
  };

  // Timer display
  const totalSeconds = selectedTime * 60;
  const remainingSeconds = Math.max(0, totalSeconds - elapsedTime);
  const remainingMinutes = remainingSeconds / 60;
  const totalCircles = Math.ceil(selectedTime / 60);

  // Time blocks
  const amHours = Array.from({ length: 9 }, (_, i) => i + 4);
  const pmHours = Array.from({ length: 12 }, (_, i) => i + 1);

  // Week days
  const weekDays = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
  const today = currentDate.getDay();

  // Time marks
  const timeMarks = [
    { value: 0, angle: -90 },
    { value: 5, angle: -60 },
    { value: 10, angle: -30 },
    { value: 15, angle: 0 },
    { value: 20, angle: 30 },
    { value: 25, angle: 60 },
    { value: 30, angle: 90 },
    { value: 35, angle: 120 },
    { value: 40, angle: 150 },
    { value: 45, angle: 180 },
    { value: 50, angle: 210 },
    { value: 55, angle: 240 },
  ];

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">TIME BLOCK</h1>
            <p className="text-sm text-gray-500">하루를 블록으로 쌓아보세요</p>
          </div>
          <div className="flex items-center gap-4">
            {user && (
              <div className="text-sm text-gray-600">
                {user.username}
              </div>
            )}
            <button
              onClick={handleLogout}
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              로그아웃
            </button>
            <div className="text-sm text-gray-500">
              {createPlan.isPending || updatePlan.isPending ? '저장 중...' : '자동 저장됨'}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: TIME GRID */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow-sm p-6">
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold">TIME GRID</h2>
                <div className="text-sm text-gray-500">
                  {currentDate.toLocaleDateString('ko-KR', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </div>
              </div>

              {/* Date - Week View */}
              <div className="flex justify-between mb-6 pb-4 border-b">
                {weekDays.map((day, idx) => (
                  <div
                    key={idx}
                    className={`flex flex-col items-center ${
                      idx === today ? 'text-black font-bold' : 'text-gray-400'
                    }`}
                  >
                    <div className="text-xs mb-1">{day}</div>
                    <div
                      className={`w-8 h-8 flex items-center justify-center rounded-full ${
                        idx === today ? 'bg-black text-white' : ''
                      }`}
                    >
                      {new Date(
                        currentDate.getTime() + (idx - today) * 24 * 60 * 60 * 1000
                      ).getDate()}
                    </div>
                  </div>
                ))}
              </div>

              {/* Top 3 Priorities */}
              <div className="mb-6">
                <h3 className="text-sm font-semibold mb-3">Top 3 Priorities</h3>
                <div className="space-y-2">
                  {priorities.map((priority, idx) => (
                    <input
                      key={idx}
                      type="text"
                      value={priority}
                      onChange={(e) => {
                        const newPriorities = [...priorities];
                        newPriorities[idx] = e.target.value;
                        setPriorities(newPriorities);
                      }}
                      placeholder={`Priority ${idx + 1}`}
                      className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-black"
                    />
                  ))}
                </div>
              </div>
            </div>

            {/* TIME BOX */}
            <div className="grid grid-cols-2 gap-6">
              {/* AM */}
              <div>
                <h3 className="text-xs font-semibold text-gray-500 mb-2">AM</h3>
                <div className="space-y-1">
                  {amHours.map((hour) => (
                    <div key={`am-${hour}`} className="flex items-center gap-2">
                      <div className="w-8 text-xs text-gray-500 text-right">{hour}</div>
                      <input
                        type="text"
                        value={timeBlocks[`am-${hour}`] || ''}
                        onChange={(e) =>
                          setTimeBlocks({ ...timeBlocks, [`am-${hour}`]: e.target.value })
                        }
                        className="flex-1 px-2 py-1.5 border border-gray-200 rounded text-xs focus:outline-none focus:ring-1 focus:ring-black"
                        placeholder="블록 입력"
                      />
                    </div>
                  ))}
                </div>
              </div>

              {/* PM */}
              <div>
                <h3 className="text-xs font-semibold text-gray-500 mb-2">PM</h3>
                <div className="space-y-1">
                  {pmHours.map((hour) => (
                    <div key={`pm-${hour}`} className="flex items-center gap-2">
                      <div className="w-8 text-xs text-gray-500 text-right">{hour}</div>
                      <input
                        type="text"
                        value={timeBlocks[`pm-${hour}`] || ''}
                        onChange={(e) =>
                          setTimeBlocks({ ...timeBlocks, [`pm-${hour}`]: e.target.value })
                        }
                        className="flex-1 px-2 py-1.5 border border-gray-200 rounded text-xs focus:outline-none focus:ring-1 focus:ring-black"
                        placeholder="블록 입력"
                      />
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* BRAIN DUMP */}
            <div className="mt-6 pt-6 border-t">
              <h3 className="text-sm font-semibold mb-3">BRAIN DUMP</h3>
              <textarea
                value={brainDump}
                onChange={(e) => setBrainDump(e.target.value)}
                className="w-full h-32 px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-black resize-none"
                placeholder="생각나는 것들을 자유롭게 적어보세요..."
              />
            </div>
          </div>

          {/* Right: Timer */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex flex-col items-center">
              <h2 className="text-lg font-bold mb-6">타이머</h2>

              {/* Timer Display */}
              <div className="relative mb-6 p-6 rounded-2xl shadow-2xl" style={{
                background: 'linear-gradient(135deg, #1f2937 0%, #111827 50%, #000000 100%)',
                boxShadow: '0 0 40px rgba(16, 185, 129, 0.15), 0 20px 50px rgba(0, 0, 0, 0.5), inset 0 0 30px rgba(16, 185, 129, 0.05)'
              }}>
                {/* Sound Icon */}
                <button
                  onClick={() => setSoundEnabled(!soundEnabled)}
                  className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center rounded-full hover:bg-opacity-70 transition-all z-10"
                  style={{
                    background: 'rgba(16, 185, 129, 0.1)',
                    border: '1px solid rgba(16, 185, 129, 0.3)',
                    boxShadow: '0 0 15px rgba(16, 185, 129, 0.2)'
                  }}
                  title={soundEnabled ? '소리 켜짐' : '소리 꺼짐'}
                >
                  {soundEnabled ? (
                    <span className="text-lg">🔊</span>
                  ) : (
                    <span className="text-lg">🔇</span>
                  )}
                </button>

                <div className="relative w-64 h-64 rounded-xl" style={{
                  background: 'radial-gradient(circle at 50% 50%, #1a1a1a 0%, #000000 70%)',
                  boxShadow: 'inset 0 0 60px rgba(0, 0, 0, 0.8), inset 0 0 30px rgba(16, 185, 129, 0.1), 0 0 20px rgba(16, 185, 129, 0.05)'
                }}>
                  {/* Digital time display */}
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <div
                        className="text-6xl font-bold tabular-nums tracking-wider"
                        style={{
                          fontFamily: "'Orbitron', 'Courier New', monospace",
                          color: '#faff00',
                          textShadow: '0 0 30px rgba(250, 255, 0, 0.95), 0 0 50px rgba(250, 255, 0, 0.8), 0 0 70px rgba(250, 255, 0, 0.5)',
                          letterSpacing: '0.15em'
                        }}
                      >
                        {formatTime(remainingSeconds)}
                      </div>
                      <div className="text-xs mt-2 font-mono" style={{
                        color: '#d4ff00',
                        textShadow: '0 0 15px rgba(212, 255, 0, 0.6)'
                      }}>
                        REMAINING
                      </div>
                    </div>
                  </div>

                  {/* Timer SVG */}
                  <svg
                    className="absolute inset-0 w-full h-full"
                    viewBox="0 0 256 256"
                  >
                    <defs>
                      <radialGradient id="cosmicGreen" cx="50%" cy="50%" r="50%">
                        <stop offset="0%" stopColor="#5eead4" stopOpacity="1" />
                        <stop offset="50%" stopColor="#10b981" stopOpacity="1" />
                        <stop offset="100%" stopColor="#0abab5" stopOpacity="1" />
                      </radialGradient>

                      <radialGradient id="cosmicGreenSmall" cx="50%" cy="50%" r="50%">
                        <stop offset="0%" stopColor="#a7f3d0" stopOpacity="0.9" />
                        <stop offset="50%" stopColor="#5eead4" stopOpacity="0.9" />
                        <stop offset="100%" stopColor="#34d399" stopOpacity="0.9" />
                      </radialGradient>

                      <filter id="cosmicGlow" x="-50%" y="-50%" width="200%" height="200%">
                        <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
                        <feMerge>
                          <feMergeNode in="coloredBlur"/>
                          <feMergeNode in="coloredBlur"/>
                          <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                      </filter>

                      <filter id="innerGlow" x="-50%" y="-50%" width="200%" height="200%">
                        <feGaussianBlur stdDeviation="3" result="blur"/>
                        <feMerge>
                          <feMergeNode in="blur"/>
                          <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                      </filter>
                    </defs>

                    {/* Multi-layer circles */}
                    {(() => {
                      const circles = [];
                      const radiuses = [110, 90, 70, 55, 40];
                      const gradients = ['cosmicGreen', 'cosmicGreenSmall', 'cosmicGreen', 'cosmicGreenSmall', 'cosmicGreen'];
                      const filters = ['cosmicGlow', 'innerGlow', 'cosmicGlow', 'innerGlow', 'cosmicGlow'];
                      const strokeWidths = [18, 15, 13, 11, 9];
                      const opacities = [0.95, 0.85, 0.75, 0.65, 0.55];

                      for (let layer = 0; layer < totalCircles && layer < 5; layer++) {
                        const layerStartMin = layer * 60;
                        const layerRemaining = Math.max(0, Math.min(remainingMinutes - layerStartMin, 60));

                        if (layerRemaining > 0) {
                          const angle = (layerRemaining / 60) * 360;
                          const radius = radiuses[layer];
                          const circumference = 2 * Math.PI * radius;
                          const dashOffset = circumference * (1 - angle / 360);

                          circles.push(
                            <circle
                              key={`layer-${layer}`}
                              cx="128"
                              cy="128"
                              r={radius}
                              fill="none"
                              stroke={`url(#${gradients[layer]})`}
                              strokeWidth={strokeWidths[layer]}
                              strokeDasharray={circumference}
                              strokeDashoffset={dashOffset}
                              strokeLinecap="round"
                              className="transition-all duration-1000 ease-linear"
                              style={{
                                filter: `url(#${filters[layer]})`,
                                opacity: opacities[layer]
                              }}
                              transform="rotate(-90 128 128)"
                            />
                          );
                        }
                      }

                      return circles;
                    })()}

                    {/* Minute marks */}
                    {Array.from({ length: 60 }, (_, i) => {
                      const angle = (i * 6 - 90) * (Math.PI / 180);
                      const innerRadius = 108;
                      const outerRadius = i % 5 === 0 ? 114 : 111;
                      const x1 = Number((128 + innerRadius * Math.cos(angle)).toFixed(2));
                      const y1 = Number((128 + innerRadius * Math.sin(angle)).toFixed(2));
                      const x2 = Number((128 + outerRadius * Math.cos(angle)).toFixed(2));
                      const y2 = Number((128 + outerRadius * Math.sin(angle)).toFixed(2));
                      return (
                        <line
                          key={`tick-${i}`}
                          x1={x1}
                          y1={y1}
                          x2={x2}
                          y2={y2}
                          stroke={i % 5 === 0 ? "#6b7280" : "#374151"}
                          strokeWidth={i % 5 === 0 ? "1.5" : "0.8"}
                          strokeLinecap="round"
                          opacity={i % 5 === 0 ? "0.7" : "0.3"}
                        />
                      );
                    })}

                    {/* Time marks text */}
                    {timeMarks.map(({ value, angle }) => {
                      const radius = 93;
                      const radian = (angle * Math.PI) / 180;
                      const x = Number((128 + radius * Math.cos(radian)).toFixed(2));
                      const y = Number((128 + radius * Math.sin(radian)).toFixed(2));
                      return (
                        <text
                          key={value}
                          x={x}
                          y={y}
                          textAnchor="middle"
                          dominantBaseline="middle"
                          className="fill-emerald-400"
                          style={{
                            fontFamily: "'Orbitron', monospace",
                            fontSize: '10px',
                            fontWeight: '600',
                            textShadow: '0 0 8px rgba(16, 185, 129, 0.6)',
                            opacity: 0.8
                          }}
                        >
                          {value}
                        </text>
                      );
                    })}
                  </svg>
                </div>
              </div>

              {/* Time Selection */}
              <div className="w-full mb-4">
                <label className="text-sm font-semibold mb-2 block">시간 설정 (분)</label>
                <div className="grid grid-cols-4 gap-2 mb-3">
                  {[15, 25, 30, 50, 60, 90, 120, 180].map((mins) => (
                    <button
                      key={mins}
                      onClick={() => {
                        setSelectedTime(mins);
                        if (!isTimerRunning) {
                          setElapsedTime(0);
                        }
                      }}
                      className={`px-3 py-2 rounded text-sm font-medium transition-colors ${
                        selectedTime === mins
                          ? 'bg-black text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      } ${mins === 50 ? 'ring-2 ring-green-400' : ''}`}
                    >
                      {mins}
                      {mins === 50 && <span className="text-xs ml-1">★</span>}
                    </button>
                  ))}
                </div>
                <input
                  type="range"
                  min="5"
                  max="180"
                  step="5"
                  value={selectedTime}
                  onChange={(e) => {
                    const mins = parseInt(e.target.value);
                    setSelectedTime(mins);
                    if (!isTimerRunning) {
                      setElapsedTime(0);
                    }
                  }}
                  className="w-full"
                />
              </div>

              {/* Recommendation */}
              <div className="w-full mb-6 px-4 py-3 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-start gap-2">
                  <span className="text-lg">💡</span>
                  <div className="text-xs text-green-800">
                    <div className="font-semibold mb-1">권장 집중 시간</div>
                    <div>50분 집중 + 10분 휴식</div>
                    <div className="text-green-600 mt-1">
                      장시간 집중 시 180분(3시간)까지 설정 가능
                    </div>
                  </div>
                </div>
              </div>

              {/* Controls */}
              <div className="w-full space-y-3">
                <button
                  onClick={handleStartTimer}
                  disabled={startTimerMutation.isPending || updateTimerMutation.isPending}
                  className="w-full bg-black text-white py-3 rounded-lg font-semibold hover:bg-gray-800 transition-colors disabled:opacity-50"
                >
                  {isTimerRunning ? '⏸ 일시정지' : '▶ 시작'}
                </button>
                <button
                  onClick={handleResetTimer}
                  disabled={updateTimerMutation.isPending}
                  className="w-full border-2 border-gray-300 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors disabled:opacity-50"
                >
                  ↻ 리셋
                </button>
              </div>

              {/* Silent Notification Settings */}
              <div className="w-full mt-6 pt-6 border-t">
                <h3 className="text-sm font-semibold mb-3">알림 설정</h3>
                <div className="space-y-2">
                  <label className="flex items-center gap-2 text-sm cursor-pointer">
                    <input
                      type="checkbox"
                      checked={soundEnabled}
                      onChange={(e) => setSoundEnabled(e.target.checked)}
                      className="rounded"
                    />
                    <span>🔊 소리 알림 (삐삐빅)</span>
                  </label>
                  <label className="flex items-center gap-2 text-sm">
                    <input type="checkbox" defaultChecked className="rounded" />
                    <span>💡 화면 플래시</span>
                  </label>
                  <label className="flex items-center gap-2 text-sm">
                    <input type="checkbox" defaultChecked className="rounded" />
                    <span>📳 진동</span>
                  </label>
                  <label className="flex items-center gap-2 text-sm">
                    <input type="checkbox" className="rounded" />
                    <span>📸 카메라 플래시</span>
                  </label>
                </div>
              </div>

              {/* Stats */}
              <div className="w-full mt-6 pt-6 border-t">
                <h3 className="text-sm font-semibold mb-3">오늘의 통계</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">완료한 블록</span>
                    <span className="font-semibold">
                      {stats ? `${stats.completed_blocks} / ${stats.total_blocks}` : '0 / 0'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">집중 시간</span>
                    <span className="font-semibold">
                      {stats
                        ? `${Math.floor(stats.total_focus_time / 60)}h ${stats.total_focus_time % 60}m`
                        : '0h 0m'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">실행률</span>
                    <span className="font-semibold">
                      {stats ? `${stats.execution_rate}%` : '0%'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
