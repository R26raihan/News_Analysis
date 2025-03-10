<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use GuzzleHttp\Client;

class DashboardController extends Controller
{
    public function index()
    {
        return view('dashboard');
    }

    public function analyze(Request $request)
    {
        $keyword = $request->input('keyword');

        if (!$keyword) {
            return redirect()->route('dashboard')->with('error', 'Masukkan kata kunci terlebih dahulu.');
        }

        $client = new Client();
        $fastapiUrl = "http://192.168.1.8:8000/analyze/" . urlencode($keyword);

        try {
            $response = $client->get($fastapiUrl, [
                'headers' => ['Accept' => 'application/json']
            ]);

            $data = json_decode($response->getBody()->getContents(), true);

            // Jika tidak ada data yang relevan
            if (isset($data['message'])) {
                return redirect()->route('dashboard')->with('error', $data['message']);
            }

            // Kirim data ke view
            return view('dashboard', [
                'data' => $data,
                'keyword' => $keyword
            ]);

        } catch (\Exception $e) {
            return redirect()->route('dashboard')->with('error', 'Gagal mengambil data: ' . $e->getMessage());
        }
    }
}
