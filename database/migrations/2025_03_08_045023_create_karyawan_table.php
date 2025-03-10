<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    /**
     * Jalankan migrasi database.
     */
    public function up()
    {
        Schema::create('karyawan', function (Blueprint $table) {
            $table->id();
            $table->string('nik')->unique();
            $table->string('email')->unique();
            $table->string('jabatan');
            $table->string('password');
            $table->timestamps();
        });
    }

    /**
     * Rollback migrasi database.
     */
    public function down()
    {
        Schema::dropIfExists('karyawan');
    }
};
