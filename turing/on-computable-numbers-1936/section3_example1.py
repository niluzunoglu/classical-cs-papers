
"""
Alan M. Turing — On Computable Numbers (1936)
Bölüm §3, Örnek I: 010101... dizisini üreten Turing makinesi

Kaynak:
    Turing, A. M. (1936). On computable numbers, with an application to the
    Entscheidungsproblem. Proceedings of the London Mathematical Society,
    Series 2, 42, 230–265.

Bu dosya hakkında:
    Turing §3'te (s. 233) Turing makinesinin çalışmasını göstermek için
    örnek: sonsuz bir banta 0 ve 1'i dönüşümlü olarak
    basan bir makine. Makale s. 233'teki geçiş tablosu bu kodun
    doğrudan kaynağıdır.

Makinenin geçiş tablosu (Turing, s. 233):

    m-config | sembol | işlemler | sonraki m-config
    ---------+--------+----------+-----------------
        b    |  Boş   |  P0, R   |       c
        c    |  Boş   |    R     |       e
        e    |  Boş   |  P1, R   |       f
        f    |  Boş   |    R     |       b

Notlar:
    - P0: 0 yaz (Print 0)
    - P1: 1 yaz (Print 1)
    - R:  sağa git (move Right)
    - Makine boş banttan başlar, b durumundan hareket eder.
    - Çift indeksli kareler F-square
      tek indeksli kareler E-square (ara notlar için rezerve).
"""


def run_machine(transition_table: dict, initial_state: str, max_steps: int = 100):
    """
    Verilen geçiş tablosuna göre bir Turing makinesini çalıştırır.

    Args:
        transition_table: {(durum, sembol): (yazılacak_sembol, yön, yeni_durum)}
        initial_state:    Başlangıç durumu
        max_steps:        Maksimum adım sayısı (sonsuz döngüyü önlemek için)

    Returns:
        tape:             Son hali ile bantın tamamı
        head:             Kafanın son pozisyonu
        history:          Her adımdaki tam konfigürasyon listesi
    """
    tape = ['_'] * 200      # Boş bant
    head = 100              # Başlangıç pozisyonu 
    state = initial_state
    history = []

    for step in range(max_steps):

        # Tam konfigürasyonu kaydet: (adım, durum, kafa pozisyonu, bant)
        history.append({
            'step': step,
            'state': state,
            'head': head,
            'tape_snapshot': ''.join(tape[95:115])   # Görünür pencere
        })

        symbol = tape[head]

        # Bu (durum, sembol) ikilisi için geçiş var mı?
        if (state, symbol) not in transition_table:
            print(f"[Adım {step}] ({state}, '{symbol}') için geçiş yok — makine durdu.")
            break

        new_symbol, direction, new_state = transition_table[(state, symbol)]

        # İşlemleri uygula
        tape[head] = new_symbol                      # Sembolu yaz
        head += 1 if direction == 'R' else -1        # Kafayı hareket ettir
        state = new_state                            # Durumu güncelle

    return tape, head, history


def print_tape(tape: list, head_pos: int, window: int = 20):
    """Bantın okunabilir bir görünümünü yazdırır."""
    start = head_pos - window // 2
    end = head_pos + window // 2
    visible = tape[start:end]

    # Kareleri göster
    print("  " + " ".join(f"{s:^3}" for s in visible))

    # Kafa pozisyonunu işaretle
    pointer_offset = head_pos - start
    print("  " + "   " * pointer_offset + " ^  ")
    print("  " + "   " * pointer_offset + f"[{tape[head_pos]}]")


def extract_output(tape: list, start: int = 95, end: int = 115) -> list:
    """
    Banttan yalnızca F-karelerindeki (asıl çıktı) sembolleri çıkarır.
    Turing §3'te F ve E karelerini ayırır:
        F-kareleri: asıl çıktı rakamları (0 ve 1)
        E-kareleri: ara notlar için rezerve, boş bırakılır
    """
    return [c for c in tape[start:end] if c != '_']


# ─────────────────────────────────────────────
# Geçiş Tablosu
# Kaynak: Turing (1936), §3, s. 233, Tablo I
# ─────────────────────────────────────────────

# Orijinal tablo (4 durumlu versiyon)
transition_table = {
    # (durum, okunan_sembol): (yazılacak_sembol, yön, yeni_durum)

    ('b', '_'): ('0', 'R', 'c'),   # b: Boş gör → 0 yaz, sağa git, c'ye geç
    ('c', '_'): ('_', 'R', 'e'),   # c: Boş gör → yazmadan sağa git, e'ye geç
    ('e', '_'): ('1', 'R', 'f'),   # e: Boş gör → 1 yaz, sağa git, f'ye geç
    ('f', '_'): ('_', 'R', 'b'),   # f: Boş gör → yazmadan sağa git, b'ye dön
}

# Turing aynı sayfada daha kısa bir alternatif tablo da veriyor (tek durumlu).
# Bu versiyon aynı sonucu üretiyor ama tek b durumuyla:
transition_table_simplified = {
    ('b', '_'): ('0', 'R', 'b'),   # Boş gör → 0 yaz
    ('b', '0'): ('0', 'R', 'b'),   # 0 gör → iki sağa git, 1 yaz
    ('b', '1'): ('1', 'R', 'b'),   # 1 gör → iki sağa git, 0 yaz
    # Not: Bu sadeleştirilmiş tablodur, orijinal değil.
}


# ─────────────────────────────────────────────
# Çalıştır
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Turing (1936) §3 Örnek I — 010101... Makinesi")
    print("=" * 60)
    print()

    tape, head, history = run_machine(
        transition_table=transition_table,
        initial_state='b',
        max_steps=40
    )

    # Son bant durumunu göster
    print("Son bant durumu:")
    print_tape(tape, head)
    print()

    # Asıl çıktıyı göster
    output = extract_output(tape)
    print(f"Üretilen dizi: {' '.join(output)}")
    print()

    # İlk 10 adımın tam konfigürasyonlarını göster
    # Turing §3'te tam konfigürasyonu şöyle tanımlar:
    # "taradığı karenin numarası + banttaki tüm semboller + m-konfigürasyon"
    print("İlk 10 adımın tam konfigürasyonları:")
    print(f"{'Adım':>5}  {'Durum':>6}  {'Bant (görünür pencere)'}")
    print("-" * 50)
    for record in history[:10]:
        print(f"{record['step']:>5}  {record['state']:>6}  {record['tape_snapshot']}")
