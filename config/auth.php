<?php

return [

    'defaults' => [
        'guard' => env('AUTH_GUARD', 'web'),
        'passwords' => 'karyawan',
    ],

    'guards' => [
        'web' => [
            'driver' => 'session',
            'provider' => 'karyawan', // Ubah dari users ke karyawan
        ],
    ],

    'providers' => [
        'karyawan' => [
            'driver' => 'eloquent',
            'model' => App\Models\Karyawan::class, // Pastikan model Karyawan ada
        ],
    ],

    'passwords' => [
        'karyawan' => [
            'provider' => 'karyawan',
            'table' => 'password_reset_tokens',
            'expire' => 60,
            'throttle' => 60,
        ],
    ],

    'password_timeout' => env('AUTH_PASSWORD_TIMEOUT', 10800),
];
