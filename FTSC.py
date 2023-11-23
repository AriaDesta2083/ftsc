import csv
from datetime import datetime
from collections import defaultdict, Counter
import os

#! PEMBUATAN ALGORITMA FUZZY TIME SERIES CHENG


def readcsv(filename):
    with open(filename) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=";")
        data = []
        tanggal = []
        for row in readCSV:
            tanggal.append(row[1])
            data.append(row[2])
    return tanggal, data


def Prepocessing(data):
    str_tanggal = data[0][1:]
    str_harga = data[1][1:]
    ex_harga = [0]
    for i in range(len(str_harga)):
        if str_harga[i] == "-":
            str_harga[i] = 0
    tanggal = [datetime.strptime(x, "%d/%m/%Y") for x in str_tanggal]
    harga = list(map(int, str_harga))
    min_harga = min([x for x in harga if x not in ex_harga])
    max_harga = max([x for x in harga if x not in ex_harga])
    new_min_harga = round(min_harga, -2)
    new_max_harga = round(max_harga / 100) * 100
    hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    for i in range(len(harga)):
        if harga[i] == 0:
            # *  SELEKSI preposessing data
            if hari[tanggal[i].weekday()] in ["Sabtu", "Minggu"]:
                harga[i] = 0
                tanggal[i] = 0
            # * NORMALISASI preposessing data
            else:
                pre = (harga[i - 1] - min_harga) / (max_harga - min_harga) * (
                    new_max_harga - new_min_harga
                ) + new_min_harga
                harga[i] = int(round(pre))
    tanggal = [x.date() for x in tanggal if x != 0]
    harga = [x for x in harga if x != 0]
    return tanggal, harga


def Filterdata(data, x):
    if x != 0:
        tanggal = [i for i in data[0][x:]]
        harga = [i for i in data[1][x:]]
        return tanggal, harga
    else:
        tanggal = [i for i in data[0]]
        harga = [i for i in data[1]]
        return tanggal, harga


def SemestaU(data):
    x = round(min(data), -2)
    d1 = abs(min(data) - x) if abs(min(data) - x) != 0 else 100
    y = round(max(data) / 100) * 100
    d2 = abs(max(data) - y) if abs(max(data) - y) != 0 else 100
    U = [min(data) - d1, max(data) + d2]
    return U, d1, d2


def Mean(harga):
    selisih = []
    for i in range(len(harga)):
        if i == len(harga) - 1:
            break
        val = harga[i + 1] - harga[i]
        selisih.append(abs(val))
    mean = round(sum(selisih) / len(harga), 5)
    return mean


def Interval(mean, u):
    panjang_interval = round(mean / 2, 5)
    jumlah_interval = round((u[1] - u[0]) / panjang_interval)
    return panjang_interval, jumlah_interval


def HimpunanFuzzy(panjang_interval, jumlah_interval, u):
    list_kelas = []
    list_bawah = []
    list_atas = []
    list_tengah = []
    dict_nilai_tengah = {}
    nilai = u[0]
    for i in range(1, jumlah_interval + 1):
        kelas = f"A{i}"
        bawah = nilai
        atas = nilai + panjang_interval
        tengah = round((bawah + atas) / 2)
        list_kelas.append(kelas)
        list_bawah.append(bawah)
        list_atas.append(atas)
        list_tengah.append(tengah)
        nilai = atas
    for i in range(1, len(list_kelas) + 1):
        dict_nilai_tengah[list_kelas[i - 1]] = list_tengah[i - 1]
    return list_kelas, list_bawah, list_atas, list_tengah, dict_nilai_tengah


def Fuzzifikasi(list_atas, list_kelas, harga):
    fuzzifikasi = []
    for nilai in harga:
        for i, k in enumerate(list_atas):
            if nilai < k:
                fuzzifikasi.append(list_kelas[i])
                break
    return fuzzifikasi


def FuzzyLogicRelationship(fuzzifikasi):
    flr = []
    for i in range(len(fuzzifikasi)):
        if i == 0:
            x = f" → {fuzzifikasi[i]}"
            flr.append(x)
        else:
            y = f"{fuzzifikasi[i-1]} → {fuzzifikasi[i]}"
            flr.append(y)
    return flr


def FuzzyLogictRelationshipGroup(fuzzifikasi):
    dictFLRG = {}
    for i in range(len(fuzzifikasi) - 1):
        grup = fuzzifikasi[i]
        relasi = fuzzifikasi[i + 1]
        if grup not in dictFLRG:
            dictFLRG[grup] = []
        dictFLRG[grup].append(relasi)
    return dictFLRG


def Pembobotan(relasi):
    newflrg = []
    bobot = []
    map_bobot = []
    for i in relasi:
        element_count = Counter(i)
        linguistik = list(element_count.keys())
        real = list(element_count.values())
        x = [f"{linguistik[i]}  ({real[i]})" for i in range(len(linguistik))]
        newflrg.append(x)
        y = [round((x / sum(real)), 5) for x in real]
        bobot.append(y)
        z = [
            [linguistik[i], round((real[i] / sum(real)), 5)]
            for i in range(len(linguistik))
        ]
        map_bobot.append(z)
    return newflrg, bobot, map_bobot


def Defuzzikasi(grup, map_bobot, dict_nilai_tengah):
    dict_deffuzikasi = {}
    list_deffuzikasi = []
    for i in range(len(map_bobot)):
        deffuz = [round(dict_nilai_tengah[i[0]] * i[1], 5) for i in map_bobot[i]]
        list_deffuzikasi.append(deffuz)
        dict_deffuzikasi[grup[i]] = round(sum(deffuz))
    return dict_deffuzikasi, list_deffuzikasi


def Peramalan(fuzzifikasi, dict_deffuzikasi):
    peramalan = []
    for i in fuzzifikasi:
        peramalan.append(dict_deffuzikasi[i])
    return peramalan


def Mape(harga, peramalan):
    list_difi = [abs(harga[i + 1] - peramalan[i]) for i in range(len(peramalan) - 1)]
    list_didi = [round(list_difi[i] / harga[i + 1], 5) for i in range(len(list_difi))]
    list_mape = [round(list_didi[i] * 100, 2) for i in range(len(list_didi))]
    nilai_mape = round(sum(list_mape) / len(list_mape), 2)
    return nilai_mape, list_difi, list_didi, list_mape


# * READ DATA
readdata = readcsv("Data.csv")

# * PREPOCESSING DATA
dataprepocessing = Prepocessing(readdata)


def tampilkan_menu():
    clear_console()
    print("=== Menu ===")
    print("1. Data Aktual")
    print("2. Semesta U")
    print("3. Interval")
    print("4. Himpunan Fuzzy")
    print("5. Fuzzifikasi")
    print("6. FLR")
    print("7. FLRG")
    print("8. Pembobotan")
    print("9. Defuzifikasi")
    print("10. Peramalan")
    print("11. Mape")
    print("0. Keluar")
    print()


def clear_console():
    # Clear console screen
    os.system("cls" if os.name == "nt" else "clear")


if __name__ == "__main__":
    # * FILTER DATA
    newdata = Filterdata(dataprepocessing, 0)
    tanggal = newdata[0]
    harga = newdata[1]
    # * SEMESTA U
    semesta = SemestaU(newdata[1])
    u = semesta[0]
    d1 = semesta[1]
    d2 = semesta[2]
    # * MEAN
    mean = Mean(harga)
    # * INTERVAL
    interval = Interval(mean, u)
    panjang_interval = interval[0]
    jumlah_interval = interval[1]

    # * HIMPUNAN FUZZY
    himpunan_fuzzy = HimpunanFuzzy(panjang_interval, jumlah_interval, u)
    list_kelas = himpunan_fuzzy[0]
    list_bawah = himpunan_fuzzy[1]
    list_atas = himpunan_fuzzy[2]
    list_tengah = himpunan_fuzzy[3]
    dict_nilai_tengah = himpunan_fuzzy[4]

    # * FUZZIFIKASI
    fuzzifikasi = Fuzzifikasi(list_atas, list_kelas, harga)

    # * FUZZY LOGIC RELATIONSHIP
    flr = FuzzyLogicRelationship(fuzzifikasi)

    # * FUZZY LOGIC RELATIONSHIP GROUP
    flrg = FuzzyLogictRelationshipGroup(fuzzifikasi)
    grup = list(flrg.keys())
    relasi = list(flrg.values())

    # * PEMBOBOTAN
    pembobotan = Pembobotan(relasi)
    newflrg = pembobotan[0]
    bobot = pembobotan[1]
    map_bobot = pembobotan[2]

    # * DEFUZZIFIKASI
    defuzzikasi = Defuzzikasi(grup, map_bobot, dict_nilai_tengah)
    dict_deffuzikasi = defuzzikasi[0]
    list_deffuzikasi = defuzzikasi[1]

    # * PERAMALAN
    peramalan = Peramalan(fuzzifikasi, dict_deffuzikasi)

    # * MAPE
    mape = Mape(harga, peramalan)
    nilai_mape = mape[0]
    list_difi = mape[1]
    list_didi = mape[2]
    list_mape = mape[3]

    def main(
        tanggal,
        harga,
        u,
        d1,
        d2,
        panjang_interval,
        jumlah_interval,
        list_kelas,
        list_bawah,
        list_atas,
        list_tengah,
        fuzzifikasi,
        flr,
        grup,
        relasi,
        newflrg,
        bobot,
        map_bobot,
        dict_deffuzikasi,
        list_deffuzikasi,
        peramalan,
        nilai_mape,
        list_difi,
        list_didi,
        list_mape,
    ):
        x = [" \t "]
        y = [f"{fuzzifikasi[-1]} → "]
        a = [str(i) for i in tanggal] + x
        b = [str(i) for i in harga] + x
        c = [str(i) for i in flr] + y
        d = x + [str(i) for i in peramalan]
        e = x + [i for i in list_difi] + x
        f = x + [i for i in list_didi] + x
        g = x + [i for i in list_mape] + [f"{nilai_mape}"]
        while True:
            tampilkan_menu()
            pilihan = input("Masukkan nomor pilihan: ")
            if pilihan == "1":
                # Implementasi untuk Pilihan 1
                clear_console()
                print(" |\tData Aktual\t|")
                print()
                print("| TANGGAL | HARGA |")
                print()
                for i in range(len(tanggal)):
                    print(f" | {harga[i-1]} |\t{tanggal[i]} | {harga[i-2]} |")
                print()
                input("Tekan Enter untuk kembali ke menu...")
            elif pilihan == "2":
                # Implementasi untuk Pilihan 2
                clear_console()
                print(" |  Semesta U | ")
                print(f"dmin\t : {min(harga)}")
                print(f"dmax\t : {max(harga)}")
                print(f"d1\t : {d1}")
                print(f"d2\t : {d2}")
                print()
                print(f"semesata u\t : {u}")
                print()
                input("Tekan Enter untuk kembali ke menu...")

            elif pilihan == "3":
                # Implementasi untuk Pilihan 2
                clear_console()
                print(" |  Interval | ")
                print(f"mean : {mean}")
                print(f"panjang interval : {panjang_interval}")
                print(f"jumlah interval : {jumlah_interval}")
                print()
                input("Tekan Enter untuk kembali ke menu...")

            elif pilihan == "4":
                # Implementasi untuk Pilihan 2
                clear_console()
                print(" |  Himpunan Fuzzy | ")
                print(f" Kelas | Batas Atas | Batas Bawah | Nilai Tengah")
                for i in range(len(list_kelas)):
                    print(
                        f" {list_kelas[i]}\t| {round(list_atas[i])} | {round(list_bawah[i])} | {round(list_tengah[i])}"
                    )
                print()
                input("Tekan Enter untuk kembali ke menu...")

            elif pilihan == "5":
                # Implementasi untuk Pilihan 2
                clear_console()

                print(" |  Fuzzifikasi | ")
                print()
                for i in range(0, len(harga), 3):
                    print(f"|{tanggal[i]} | {harga[i]} | {fuzzifikasi[i]} |")
                print()
                input("Tekan Enter untuk kembali ke menu...")

            elif pilihan == "6":
                # Implementasi untuk Pilihan 2
                clear_console()
                print(" |  FLR | ")
                print()
                for i in range(len(harga)):
                    print(f"| {tanggal[i]} | {harga[i]} | {flr[i]}\t|")
                print()

                input("Tekan Enter untuk kembali ke menu...")
            elif pilihan == "7":
                # Implementasi untuk Pilihan 2
                clear_console()
                print(" |  FLRG | ")
                print()
                for i in range(len(grup)):
                    print(f"{grup[i]}\n\t{newflrg[i]}\n\t{relasi[i]}")
                print()
                input("Tekan Enter untuk kembali ke menu...")

            elif pilihan == "8":
                # Implementasi untuk Pilihan 2
                clear_console()
                print(" |  Pembobotan | ")
                print()
                for i in range(len(bobot)):
                    print(f"{grup[i]}\n\t{newflrg[i]}\n\t{relasi[i]}\n\t{bobot[i]}")
                print()
                print()
                input("Tekan Enter untuk kembali ke menu...")

            elif pilihan == "9":
                # Implementasi untuk Pilihan 2
                clear_console()
                print(" |  Defuzifikasi | ")
                print()
                for i in range(len(grup)):
                    print(
                        f"{grup[i]}\n\t{newflrg[i]}\n\t{bobot[i]}\n\t{list_deffuzikasi[i]}"
                    )
                input("Tekan Enter untuk kembali ke menu...")

            elif pilihan == "10":
                # Implementasi untuk Pilihan 2
                clear_console()
                print(" |  Peramalan | ")
                for i in range(len(a)):
                    print(f"| {a[i]} | {b[i]} | {c[i]}\t| {d[i]}|")
                print("hasil peramalan  ")
                input("Tekan Enter untuk kembali ke menu...")

            elif pilihan == "11":
                # Implementasi untuk Pilihan 2
                clear_console()
                print(" |  Mape | ")
                print()
                for i in range(len(e)):
                    print(f"| {a[i]} | {b[i]} | {d[i]} | {e[i]} | {f[i]}\t| {g[i]} |")
                print()
                input("Tekan Enter untuk kembali ke menu...")

            elif pilihan == "0":
                clear_console()
                print("Keluar dari program. Sampai jumpa!")
                break
            else:
                clear_console()
                print("Pilihan tidak valid. Silakan coba lagi.")

    main(
        tanggal,
        harga,
        u,
        d1,
        d2,
        panjang_interval,
        jumlah_interval,
        list_kelas,
        list_bawah,
        list_atas,
        list_tengah,
        fuzzifikasi,
        flr,
        grup,
        relasi,
        newflrg,
        bobot,
        map_bobot,
        dict_deffuzikasi,
        list_deffuzikasi,
        peramalan,
        nilai_mape,
        list_difi,
        list_didi,
        list_mape,
    )
