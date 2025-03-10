<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;

class Karyawan extends Authenticatable
{
    use HasFactory, Notifiable;

    protected $table = 'karyawan'; // Pastikan Laravel tahu bahwa ini tabel yang digunakan

    protected $primaryKey = 'id'; // Sesuai dengan kolom ID utama

    protected $fillable = [
        'id', 'email', 'jabatan', 'password'
    ];

    protected $hidden = ['password'];

    public function getAuthPassword()
    {
        return $this->password;
    }
}

