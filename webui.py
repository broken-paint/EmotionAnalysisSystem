HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>表情分析系统 - 结果展示</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdn.jsdelivr.net/npm/font-awesome@4.7.0/css/font-awesome.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.8/dist/chart.umd.min.js"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#3B82F6',
                        secondary: '#10B981',
                        neutral: '#6B7280',
                        emotion: {
                            happy: '#FBBF24',
                            sad: '#60A5FA',
                            angry: '#EF4444',
                            surprised: '#F59E0B',
                            fear: '#8B5CF6',
                            disgust: '#10B981',
                            neutral: '#6B7280'
                        }
                    },
                    fontFamily: {
                        sans: ['Inter', 'system-ui', 'sans-serif'],
                    },
                }
            }
        }
    </script>
    <style type="text/tailwindcss">
        @layer utilities {
            .content-auto {
                content-visibility: auto;
            }
            .emotion-card {
                @apply rounded-xl p-4 shadow-md transition-all duration-300 hover:shadow-lg;
            }
            .stat-card {
                @apply bg-white rounded-xl p-6 shadow-md border border-gray-100;
            }
        }
    </style>
</head>
<body class="bg-gray-50 font-sans text-gray-800">
    <!-- 顶部导航 -->
    <header class="bg-white shadow-sm sticky top-0 z-50">
        <div class="container mx-auto px-4 py-4 flex justify-between items-center">
            <div class="flex items-center space-x-2">
                <i class="fa fa-smile-o text-primary text-2xl"></i>
                <h1 class="text-xl font-bold text-gray-800">表情分析系统</h1>
            </div>
            <div class="text-sm text-gray-500">
                <span id="last-update">最后更新: 加载中...</span>
            </div>
        </div>
    </header>

    <main class="container mx-auto px-4 py-8">
        <!-- 概览统计 -->
        <section class="mb-10">
            <h2 class="text-2xl font-bold mb-6">表情分析概览</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="stat-card">
                    <div class="flex justify-between items-start">
                        <div>
                            <p class="text-neutral text-sm">检测到的人脸总数</p>
                            <h3 class="text-3xl font-bold mt-1" id="total-faces">0</h3>
                        </div>
                        <div class="bg-blue-100 p-3 rounded-full">
                            <i class="fa fa-user text-primary text-xl"></i>
                        </div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="flex justify-between items-start">
                        <div>
                            <p class="text-neutral text-sm">主要表情</p>
                            <h3 class="text-3xl font-bold mt-1" id="dominant-emotion">中性</h3>
                        </div>
                        <div class="bg-yellow-100 p-3 rounded-full">
                            <i class="fa fa-smile-o text-emotion-happy text-xl"></i>
                        </div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="flex justify-between items-start">
                        <div>
                            <p class="text-neutral text-sm">分析时长</p>
                            <h3 class="text-3xl font-bold mt-1" id="analysis-duration">0分钟</h3>
                        </div>
                        <div class="bg-green-100 p-3 rounded-full">
                            <i class="fa fa-clock-o text-secondary text-xl"></i>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- 表情分布和趋势 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-10">
            <!-- 表情分布饼图 -->
            <section class="bg-white rounded-xl p-6 shadow-md">
                <h2 class="text-xl font-bold mb-4">表情分布</h2>
                <div class="h-80">
                    <canvas id="emotion-distribution-chart"></canvas>
                </div>
            </section>

            <!-- 表情趋势线图 -->
            <section class="bg-white rounded-xl p-6 shadow-md">
                <h2 class="text-xl font-bold mb-4">表情趋势</h2>
                <div class="h-80">
                    <canvas id="emotion-trend-chart"></canvas>
                </div>
            </section>
        </div>

        <!-- 检测到的表情样本 -->
        <section class="mb-10">
            <h2 class="text-2xl font-bold mb-6">检测到的表情样本</h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6" id="emotion-samples">
                <!-- 表情样本卡片将通过JS动态生成 -->
            </div>
        </section>

        <!-- 分析报告 -->
        <section class="bg-white rounded-xl p-6 shadow-md mb-10">
            <h2 class="text-2xl font-bold mb-4">情绪分析报告</h2>
            <div class="prose max-w-none">
                <p id="analysis-report">正在生成分析报告...</p>
            </div>
        </section>
    </main>

    <footer class="bg-gray-800 text-white py-8">
        <div class="container mx-auto px-4">
            <div class="flex flex-col md:flex-row justify-between items-center">
                <div class="mb-4 md:mb-0">
                    <div class="flex items-center space-x-2">
                        <i class="fa fa-smile-o text-primary text-xl"></i>
                        <span class="font-bold">表情分析系统</span>
                    </div>
                    <p class="text-gray-400 text-sm mt-2">基于FER2013数据集的表情识别系统</p>
                </div>
                <div class="text-gray-400 text-sm">
                    © 2023 表情分析系统 | 使用PyTorch和OpenCV构建
                </div>
            </div>
        </div>
    </footer>

    <script>
        // 模拟表情识别数据
        const emotionData = {
            totalFaces: 247,
            dominantEmotion: "开心",
            duration: "45",
            lastUpdate: "2023-06-15 14:30:22",
            distribution: {
                开心: 42,
                悲伤: 15,
                愤怒: 8,
                惊讶: 18,
                恐惧: 5,
                厌恶: 2,
                中性: 10
            },
            trend: {
                time: ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00"],
                开心: [35, 40, 38, 45, 42, 42],
                悲伤: [18, 16, 15, 12, 14, 15],
                愤怒: [10, 8, 9, 7, 8, 8],
                中性: [12, 10, 11, 10, 9, 10]
            },
            samples: [
                { emotion: "开心", image: "https://picsum.photos/seed/happy1/300/300" },
                { emotion: "悲伤", image: "https://picsum.photos/seed/sad1/300/300" },
                { emotion: "愤怒", image: "https://picsum.photos/seed/angry1/300/300" },
                { emotion: "惊讶", image: "https://picsum.photos/seed/surprise1/300/300" },
                { emotion: "中性", image: "https://picsum.photos/seed/neutral1/300/300" },
                { emotion: "开心", image: "https://picsum.photos/seed/happy2/300/300" },
                { emotion: "悲伤", image: "https://picsum.photos/seed/sad2/300/300" },
                { emotion: "惊讶", image: "https://picsum.photos/seed/surprise2/300/300" }
            ]
        };

        // 初始化页面数据
        document.addEventListener('DOMContentLoaded', function() {
            // 更新统计数据
            document.getElementById('total-faces').textContent = emotionData.totalFaces;
            document.getElementById('dominant-emotion').textContent = emotionData.dominantEmotion;
            document.getElementById('analysis-duration').textContent = emotionData.duration + "分钟";
            document.getElementById('last-update').textContent = "最后更新: " + emotionData.lastUpdate;

            // 生成表情样本卡片
            const samplesContainer = document.getElementById('emotion-samples');
            emotionData.samples.forEach(sample => {
                const emotionClass = sample.emotion.toLowerCase();
                const card = document.createElement('div');
                card.className = 'emotion-card bg-white';
                card.innerHTML = `
                    <div class="relative overflow-hidden rounded-lg mb-3">
                        <img src="${sample.image}" alt="${sample.emotion}" class="w-full h-48 object-cover">
                        <div class="absolute bottom-0 left-0 right-0 bg-black bg-opacity-60 text-white p-2 text-sm">
                            ${sample.emotion}
                        </div>
                    </div>
                    <div class="flex items-center justify-center">
                        <span class="inline-block px-3 py-1 rounded-full text-xs font-medium bg-emotion-${emotionClass}/20 text-emotion-${emotionClass}">
                            ${sample.emotion}
                        </span>
                    </div>
                `;
                samplesContainer.appendChild(card);
            });

            // 生成分析报告
            generateReport();

            // 初始化图表
            initDistributionChart();
            initTrendChart();
        });

        // 生成分析报告
        function generateReport() {
            const reportElement = document.getElementById('analysis-report');
            const happyPercent = emotionData.distribution.开心;
            
            let reportText = `<p>在过去${emotionData.duration}分钟的监测中，共检测到${emotionData.totalFaces}张人脸图像。</p>`;
            reportText += `<p>主要表情为<strong>${emotionData.dominantEmotion}</strong>，占比${happyPercent}%，表明整体情绪状态较为积极。</p>`;
            
            if (happyPercent > 30) {
                reportText += `<p>从趋势来看，积极情绪保持稳定，未出现明显波动，显示良好的情绪状态。</p>`;
            } else {
                reportText += `<p>需要注意的是，积极情绪占比不高，建议进一步观察和干预。</p>`;
            }
            
            reportText += `<p>表情分布较为均衡，但${emotionData.dominantEmotion}情绪占据主导地位，符合正常的情绪表现范围。</p>`;
            reportElement.innerHTML = reportText;
        }

        // 初始化表情分布饼图
        function initDistributionChart() {
            const ctx = document.getElementById('emotion-distribution-chart').getContext('2d');
            const labels = Object.keys(emotionData.distribution);
            const data = Object.values(emotionData.distribution);
            const colors = [
                '#FBBF24', // 开心
                '#60A5FA', // 悲伤
                '#EF4444', // 愤怒
                '#F59E0B', // 惊讶
                '#8B5CF6', // 恐惧
                '#10B981', // 厌恶
                '#6B7280'  // 中性
            ];

            new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: colors,
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right'
                        }
                    }
                }
            });
        }

        // 初始化表情趋势线图
        function initTrendChart() {
            const ctx = document.getElementById('emotion-trend-chart').getContext('2d');
            const emotions = Object.keys(emotionData.trend).filter(key => key !== 'time');
            const datasets = emotions.map((emotion, index) => {
                const colorMap = {
                    '开心': '#FBBF24',
                    '悲伤': '#60A5FA',
                    '愤怒': '#EF4444',
                    '中性': '#6B7280'
                };
                
                return {
                    label: emotion,
                    data: emotionData.trend[emotion],
                    borderColor: colorMap[emotion] || `hsl(${index * 60}, 70%, 50%)`,
                    backgroundColor: `${colorMap[emotion] || `hsl(${index * 60}, 70%, 50%)`}33`,
                    tension: 0.3,
                    fill: false
                };
            });

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: emotionData.trend.time,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: '占比 (%)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: '时间'
                            }
                        }
                    }
                }
            });
        }
    </script>
</body>
</html>
"""