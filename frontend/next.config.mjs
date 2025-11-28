/** @type {import('next').NextConfig} */
const nextConfig = {
    async rewrites() {
        return [
            {
                source: '/api/:path*', // Все запросы на /api/...
                destination: 'http://127.0.0.1:8000/api/v1/:path*', // ...перенаправляем на Бэкенд
            },
        ]
    },
};

export default nextConfig;