<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Analisis Berita</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: 'Inter', sans-serif;
        }
        .shadow-custom {
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
</head>
<body class="bg-gray-50 antialiased">

    <!-- Navbar -->
    <nav class="bg-gradient-to-r from-blue-600 to-blue-800 p-4 text-white shadow-md">
        <div class="container mx-auto flex justify-between items-center">
            <h1 class="text-2xl font-bold tracking-tight">Dashboard Analisis Berita</h1>
            <form action="{{ route('logout') }}" method="POST">
                @csrf
                <button type="submit" class="bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-5 rounded-lg transition duration-200">
                    Logout
                </button>
            </form>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="container mx-auto mt-8 px-4">
        <div class="bg-white p-6 rounded-xl shadow-custom">
            <h2 class="text-2xl font-bold text-gray-800 mb-6">Analisis Sentimen Berita</h2>

            <!-- Pesan Error atau Sukses -->
            @if (session('error'))
                <div class="bg-red-50 border-l-4 border-red-400 text-red-700 p-4 rounded mb-6">
                    {{ session('error') }}
                </div>
            @endif

            <!-- Form untuk memasukkan keyword -->
            <div class="mb-8">
                <h3 class="text-xl font-semibold text-gray-800 mb-4">Cari Berita</h3>
                <form action="{{ route('analyze-news') }}" method="POST" class="flex space-x-2">
                    @csrf
                    <input type="text" name="keyword" placeholder="Masukkan kata kunci..." required
                        class="p-3 border border-gray-200 rounded-lg w-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition">
                    <button type="submit"
                        class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition duration-200">
                        Cari
                    </button>
                </form>
            </div>

            <!-- Hasil Analisis -->
            @if(isset($data))
                <div>
                    <div class="flex items-center justify-between mb-6">
                        <h3 class="text-xl font-semibold text-gray-800">Hasil Analisis: {{ $keyword }}</h3>
                        <p class="text-gray-600">Total Berita: <span class="font-semibold text-gray-800">{{ $data['total_items'] }}</span></p>
                    </div>

                    <!-- Ringkasan Sentimen -->
                    <div class="mb-10">
                        <h4 class="text-lg font-semibold text-gray-700 mb-4">Ringkasan Sentimen</h4>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                            @foreach($data['sentiment_summary'] as $sentiment => $info)
                                <div class="bg-gray-50 p-5 rounded-lg shadow-custom border border-gray-100">
                                    <h5 class="font-bold text-lg {{ $sentiment === 'Positif' ? 'text-green-600' : ($sentiment === 'Negatif' ? 'text-red-600' : 'text-gray-600') }}">
                                        {{ $sentiment }}
                                    </h5>
                                    <p class="text-gray-600 mt-2">Jumlah: <span class="font-semibold">{{ $info['count'] }}</span></p>
                                    <p class="text-gray-600">Persentase: <span class="font-semibold">{{ number_format($info['percentage'], 2) }}%</span></p>
                                    @if(!empty($info['examples']))
                                        <p class="mt-3 text-sm font-semibold text-gray-700">Contoh:</p>
                                        <ul class="list-disc pl-5 text-sm text-gray-600">
                                            @foreach($info['examples'] as $example)
                                                <li>{{ $example['text'] }} ({{ $example['source'] }})</li>
                                            @endforeach
                                        </ul>
                                    @endif
                                </div>
                            @endforeach
                        </div>
                    </div>

                    <!-- Diagram Distribusi Sumber -->
                    <div class="mb-10">
                        <h4 class="text-lg font-semibold text-gray-700 mb-4">Distribusi Sumber</h4>
                        <div class="bg-white p-6 rounded-lg shadow-custom h-96">
                            <canvas id="sourceChart"></canvas>
                        </div>
                    </div>

                    <!-- Diagram Distribusi Kategori -->
                    <div class="mb-10">
                        <h4 class="text-lg font-semibold text-gray-700 mb-4">Distribusi Kategori</h4>
                        <div class="bg-white p-6 rounded-lg shadow-custom h-96">
                            <canvas id="categoryChart"></canvas>
                        </div>
                    </div>

                    <!-- Detail Hasil -->
                    <div>
                        <h4 class="text-lg font-semibold text-gray-700 mb-4">Detail Hasil</h4>
                        <div class="overflow-x-auto bg-white rounded-lg shadow-custom">
                            <table class="min-w-full">
                                <thead>
                                    <tr class="bg-gray-100 text-gray-700 text-left">
                                        <th class="p-4 font-semibold">Sumber</th>
                                        <th class="p-4 font-semibold">Kategori</th>
                                        <th class="p-4 font-semibold">Judul</th>
                                        <th class="p-4 font-semibold">Sentimen</th>
                                        <th class="p-4 font-semibold">Skor</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-gray-100">
                                    @foreach($data['detailed_results'] as $result)
                                        <tr class="hover:bg-gray-50 transition">
                                            <td class="p-4">{{ $result['source'] }}</td>
                                            <td class="p-4">{{ $result['category'] }}</td>
                                            <td class="p-4">{{ $result['text'] }}</td>
                                            <td class="p-4 {{ $result['sentiment'] === 'Positif' ? 'text-green-600' : ($result['sentiment'] === 'Negatif' ? 'text-red-600' : 'text-gray-600') }}">
                                                {{ $result['sentiment'] }}
                                            </td>
                                            <td class="p-4">{{ number_format($result['score'], 2) }}</td>
                                        </tr>
                                    @endforeach
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            @endif
        </div>
    </div>

    <!-- Script untuk Chart.js -->
    <script>
        const colorPalette = [
            'rgba(59, 130, 246, 0.8)',  // Biru
            'rgba(16, 185, 129, 0.8)',  // Hijau
            'rgba(239, 68, 68, 0.8)',   // Merah
            'rgba(249, 115, 22, 0.8)',  // Oranye
            'rgba(139, 92, 246, 0.8)',  // Ungu
            'rgba(234, 179, 8, 0.8)',   // Kuning
        ];

        const sourceData = {
            labels: {!! json_encode(array_keys($data['source_distribution'] ?? [])) !!},
            datasets: [{
                label: 'Distribusi Sumber',
                data: {!! json_encode(array_values($data['source_distribution'] ?? [])) !!},
                backgroundColor: colorPalette.slice(0, Object.keys( {!! json_encode($data['source_distribution'] ?? []) !!}).length),
                borderColor: colorPalette.slice(0, Object.keys( {!! json_encode($data['source_distribution'] ?? []) !!}).length).map(color => color.replace('0.8', '1')),
                borderWidth: 1,
                borderRadius: 6,
                barThickness: 40
            }]
        };

        const categoryData = {
            labels: {!! json_encode(array_keys($data['category_distribution'] ?? [])) !!},
            datasets: [{
                label: 'Distribusi Kategori',
                data: {!! json_encode(array_values($data['category_distribution'] ?? [])) !!},
                backgroundColor: colorPalette.slice(0, Object.keys( {!! json_encode($data['category_distribution'] ?? []) !!}).length),
                borderColor: colorPalette.slice(0, Object.keys( {!! json_encode($data['category_distribution'] ?? []) !!}).length).map(color => color.replace('0.8', '1')),
                borderWidth: 1
            }]
        };

        const sourceCtx = document.getElementById('sourceChart').getContext('2d');
        new Chart(sourceCtx, {
            type: 'bar',
            data: sourceData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    title: {
                        display: true,
                        text: 'Distribusi Berita Berdasarkan Sumber',
                        font: { size: 16, weight: 'bold' },
                        padding: { bottom: 20 }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleFont: { size: 14 },
                        bodyFont: { size: 12 }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Jumlah Berita', font: { size: 12 } },
                        grid: { color: 'rgba(0, 0, 0, 0.05)' }
                    },
                    x: { grid: { display: false } }
                },
                layout: { padding: 20 }
            }
        });

        const categoryCtx = document.getElementById('categoryChart').getContext('2d');
        new Chart(categoryCtx, {
            type: 'pie',
            data: categoryData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { padding: 20, font: { size: 12 } }
                    },
                    title: {
                        display: true,
                        text: 'Distribusi Berita Berdasarkan Kategori',
                        font: { size: 16, weight: 'bold' },
                        padding: { bottom: 20 }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleFont: { size: 14 },
                        bodyFont: { size: 12 }
                    }
                },
                layout: { padding: 20 }
            }
        });
    </script>

</body>
</html>
