'use client';

/**
 * Login Page - Google and Kakao OAuth
 */

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { GoogleLogin, CredentialResponse } from '@react-oauth/google';
import { apiClient } from '@/lib/api/client';
import { useAuthStore } from '@/lib/store/authStore';

declare global {
  interface Window {
    Kakao: any;
  }
}

export default function LoginPage() {
  const router = useRouter();
  const { setUser, isAuthenticated } = useAuthStore();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/wireframe');
    }
  }, [isAuthenticated, router]);

  // Initialize Kakao SDK
  useEffect(() => {
    if (typeof window !== 'undefined' && window.Kakao && !window.Kakao.isInitialized()) {
      const kakaoAppKey = process.env.NEXT_PUBLIC_KAKAO_APP_KEY;
      if (kakaoAppKey) {
        window.Kakao.init(kakaoAppKey);
      }
    }
  }, []);

  // Google Login Handler
  const handleGoogleSuccess = async (credentialResponse: CredentialResponse) => {
    try {
      if (!credentialResponse.credential) {
        throw new Error('No credential received');
      }

      const result = await apiClient.loginWithGoogle(credentialResponse.credential);
      setUser(result.user);
      router.push('/wireframe');
    } catch (error) {
      console.error('Google login failed:', error);
      alert('Google 로그인에 실패했습니다. 다시 시도해주세요.');
    }
  };

  const handleGoogleError = () => {
    alert('Google 로그인에 실패했습니다.');
  };

  // Kakao Login Handler
  const handleKakaoLogin = () => {
    if (!window.Kakao) {
      alert('Kakao SDK가 로드되지 않았습니다.');
      return;
    }

    window.Kakao.Auth.login({
      success: async (authObj: any) => {
        try {
          const result = await apiClient.loginWithKakao(authObj.access_token);
          setUser(result.user);
          router.push('/wireframe');
        } catch (error) {
          console.error('Kakao login failed:', error);
          alert('Kakao 로그인에 실패했습니다. 다시 시도해주세요.');
        }
      },
      fail: (err: any) => {
        console.error('Kakao login failed:', err);
        alert('Kakao 로그인에 실패했습니다.');
      },
    });
  };

  return (
    <>
      {/* Kakao SDK */}
      <script src="https://developers.kakao.com/sdk/js/kakao.js" async />

      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-black">
        <div className="max-w-md w-full p-8 bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700">
          {/* Logo */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-white mb-2">
              TIME<span className="text-cyan-400">LOCK</span>
            </h1>
            <p className="text-gray-400">하루를 블록으로 쌓아보세요</p>
          </div>

          {/* Login Buttons */}
          <div className="space-y-4">
            {/* Google Login */}
            <div className="flex justify-center">
              <GoogleLogin
                onSuccess={handleGoogleSuccess}
                onError={handleGoogleError}
                theme="filled_blue"
                size="large"
                text="continue_with"
                width="384"
                locale="ko"
              />
            </div>

            {/* Kakao Login */}
            <button
              onClick={handleKakaoLogin}
              className="w-full flex items-center justify-center gap-3 px-6 py-3 bg-[#FEE500] hover:bg-[#FDD835] text-gray-900 font-medium rounded-lg transition-colors"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M12 3c5.799 0 10.5 3.664 10.5 8.185 0 4.52-4.701 8.184-10.5 8.184a13.5 13.5 0 0 1-1.727-.11l-4.408 2.883c-.501.265-.678.236-.472-.413l.892-3.678c-2.88-1.46-4.785-3.99-4.785-6.866C1.5 6.665 6.201 3 12 3z"
                />
              </svg>
              Kakao로 시작하기
            </button>
          </div>

          {/* Footer */}
          <p className="text-center text-gray-500 text-sm mt-8">
            로그인하면{' '}
            <span className="text-gray-400">서비스 이용약관</span>과{' '}
            <span className="text-gray-400">개인정보 처리방침</span>에 동의하게 됩니다.
          </p>
        </div>
      </div>
    </>
  );
}
