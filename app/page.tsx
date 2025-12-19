export default function Home() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">TIMELOCK</h1>
        <p className="text-lg text-gray-600">독서실에서도 눈치 안 보고 쓰는 무음 타이머</p>
        <a
          href="/prototype"
          className="mt-8 inline-block bg-black text-white px-6 py-3 rounded-lg hover:bg-gray-800"
        >
          무음 알림 프로토타입 →
        </a>
      </div>
    </div>
  );
}
