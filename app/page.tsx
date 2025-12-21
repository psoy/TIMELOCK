export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Hero Section */}
      <div className="max-w-6xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h1 className="text-6xl font-black mb-6 bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
            TIME BLOCK
          </h1>
          <p className="text-2xl text-gray-700 mb-4">
            하루를 블록으로 쌓아보세요
          </p>
          <p className="text-lg text-gray-500 max-w-2xl mx-auto">
            15분 단위로 쌓는 집중 블록, 독서실에서도 눈치 안 보고 쓰는 무음 타이머
          </p>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white rounded-2xl p-8 shadow-sm hover:shadow-md transition-shadow">
            <div className="text-4xl mb-4">🧱</div>
            <h3 className="text-xl font-bold mb-3">블록으로 쌓는 시간</h3>
            <p className="text-gray-600">
              1시간을 15분 단위로 나눠 레고 블록처럼 쌓아가세요. 작은 블록들이 모여 큰 성취가 됩니다.
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-sm hover:shadow-md transition-shadow">
            <div className="text-4xl mb-4">🔇</div>
            <h3 className="text-xl font-bold mb-3">무음 알림</h3>
            <p className="text-gray-600">
              화면 플래시, 진동, 카메라 플래시로 조용히 알려드립니다. 독서실, 도서관 어디서든 눈치 보지 마세요.
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-sm hover:shadow-md transition-shadow">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-xl font-bold mb-3">집중 시간 추적</h3>
            <p className="text-gray-600">
              오늘 쌓은 블록, 완료한 시간, 실행률을 한눈에 확인하세요. 매일의 성장을 기록합니다.
            </p>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center">
          <a
            href="/wireframe"
            className="inline-block bg-black text-white px-12 py-4 rounded-xl text-lg font-bold hover:bg-gray-800 transition-colors shadow-lg hover:shadow-xl"
          >
            지금 시작하기 →
          </a>
          <p className="mt-4 text-sm text-gray-500">
            가입 없이 바로 시작 • 완전 무료
          </p>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-8 text-center text-sm text-gray-500">
        <p>© 2025 TIME BLOCK. 하루를 블록으로 쌓아보세요.</p>
      </footer>
    </div>
  );
}
