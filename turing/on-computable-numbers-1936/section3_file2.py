"""
Alan M. Turing — On Computable Numbers (1936)
Bölüm §3, Örnek II: 001011011101111... dizisini üreten Turing makinesi

Kaynak:
    Turing, A. M. (1936). On computable numbers, with an application to the
    Entscheidungsproblem. Proceedings of the London Mathematical Society,
    Series 2, 42, 230–265.

Bu dosya hakkında:
    Turing §3'te (s. 234–235) ikinci ve daha karmaşık örneğini verir.
    Bu makine şu diziyi üretir:

        0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, ...

    Desen: Bir 0, ardından giderek artan sayıda 1.
    
        0               (sıfır 1)
        0, 1            (bir 1)
        0, 1, 1         (iki 1)
        0, 1, 1, 1      (üç 1)
        ...

    Bu makine, ilk örnekten farklı olarak bir şeyi SAYMAK zorunda.
    Turing makinesinde sayaç veya bellek yoktur. Makine bu sorunu
    bantı bellek olarak kullanarak çözer — ara işaretler (x) koyar,
    onları sayar ve siler.

    Bu dosya, Turing'in s. 234'teki geçiş tablosunu doğrudan
    Python'a çevirmektedir.

Makinenin geçiş tablosu (Turing, s. 234):

    m-config | sembol      | işlemler                     | sonraki m-config
    ---------+-------------+------------------------------+-----------------
        b    |    —        | Pa, R, Pa, R, P0, R, R, P0,  |       o
             |             | L, L                         |
    ---------+-------------+------------------------------+-----------------
        o    |    1        | R, Px, L, L, L               |       o
        o    |    0        |    —                         |       q
    ---------+-------------+------------------------------+-----------------
        q    | 0 veya 1    |    R, R                      |       q
        q    |    Boş      |    P1, L                     |       p
    ---------+-------------+------------------------------+-----------------
        p    |    x        |    E, R                      |       q
        p    |    a        |    R                         |       f
        p    |    Boş      |    L, L                      |       p
    ---------+-------------+------------------------------+-----------------
        f    |  Herhangi   |    R, R                      |       f
        f    |    Boş      |    P0, L, L                  |       o

Semboller:
    a  — Başlangıç işaretleyicisi (F-karelerinde sabit kalır)
    x  — Geçici sayaç işareti (E-karelerinde, silinebilir)
    0  — Asıl çıktı (F-karesi)
    1  — Asıl çıktı (F-karesi)
    _  — Boş kare

Notlar:
    - P<s>: s sembolünü yaz (Print)
    - E:    sembolu sil (Erase) — Turing'in modelinde boşlukla aynı
    - R:    sağa git (Right)
    - L:    sola git (Left)
    - Makine her turda bir önceki turdan bir fazla 1 üretir.
      Bunu bantı bellek olarak kullanarak başarır.

Önemli kavram — Bant Bellek Olarak:
    Bu ikinci örnek, Turing makinesinin en kritik özelliğini gösterir:
    Makinenin ayrı bir belleği yoktur. Bant hem çıktı hem bellek.
    x işaretleri "şu ana kadar bu turu kaç kez tekrarladım" 
    bilgisini bantın üzerinde taşır. Bu fikir Von Neumann'ın 
    stored-program (depolanmış program) mimarisinin öncülüdür.
"""


def run_machine(transition_table: dict, initial_state: str, max_steps: int = 500):
    """
    Verilen geçiş tablosuna göre bir Turing makinesini çalıştırır.

    Args:
        transition_table: {(durum, sembol): [(işlem, değer), ...]}
                          İşlemler: 'P' (yaz), 'E' (sil), 'R' (sağa), 'L' (sola)
        initial_state:    Başlangıç durumu
        max_steps:        Maksimum adım sayısı

    Returns:
        tape:    Son hali ile bantın tamamı
        history: Her adımdaki tam konfigürasyon listesi
    """
    tape = ['_'] * 500
    head = 250
    state = initial_state
    history = []

    for step in range(max_steps):

        history.append({
            'step': step,
            'state': state,
            'head': head,
            'tape_snapshot': ''.join(tape[245:275])
        })

        symbol = tape[head]

        # Bu (durum, sembol) ikilisi için geçiş var mı?
        if (state, symbol) not in transition_table:
            print(f"[Adım {step}] ({state}, '{symbol}') için geçiş yok — makine durdu.")
            break

        operations, new_state = transition_table[(state, symbol)]

        # İşlemleri sırayla uygula
        for op, val in operations:
            if op == 'P':          # Print — yaz
                tape[head] = val
            elif op == 'E':        # Erase — sil
                tape[head] = '_'
            elif op == 'R':        # Right — sağa git
                head += 1
            elif op == 'L':        # Left — sola git
                head -= 1

        state = new_state

    return tape, history


def extract_output(tape: list) -> list:
    """
    Banttan yalnızca asıl çıktı sembollerini çıkarır.
    
    Turing §3'te F ve E karelerini şöyle ayırır:
        F-kareleri: 0 ve 1 içerir (asıl çıktı, kalıcı)
        E-kareleri: a, x gibi geçici işaretler içerir (silinebilir)
    
    Biz burada yalnızca 0 ve 1'leri alıyoruz.
    """
    return [c for c in tape if c in ('0', '1')]


def print_tape(tape: list, head: int, window: int = 30):
    """Bantın okunabilir görünümünü yazdırır."""
    start = max(0, head - window // 2)
    end = min(len(tape), head + window // 2)
    visible = tape[start:end]
    pointer_offset = head - start

    print("  " + " ".join(f"{s:^3}" for s in visible))
    print("  " + "   " * pointer_offset + " ^ ")


# ─────────────────────────────────────────────
# Geçiş Tablosu
# Kaynak: Turing (1936), §3, s. 234, Tablo II
#
# Format: {(durum, sembol): ([(op, değer), ...], yeni_durum)}
# ─────────────────────────────────────────────

transition_table = {

    # ── b durumu ─────────────────────────────────────────────────────────
    # Başlangıç. Banta a, a, 0, _, 0 yazar ve o durumuna geçer.
    # Turing s. 234: "b | Pa, R, Pa, R, P0, R, R, P0, L, L | o"
    ('b', '_'): (
        [('P', 'a'), ('R', None),           # İlk a'yı yaz, sağa git
         ('P', 'a'), ('R', None),           # İkinci a'yı yaz, sağa git
         ('P', '0'), ('R', None),           # İlk 0'ı yaz, sağa git
                     ('R', None),           # Bir kare atla (E-karesi)
         ('P', '0'), ('L', None),           # İkinci 0'ı yaz, sola dön
                     ('L', None)],          # Bir kare daha sola
        'o'
    ),

    # ── o durumu ─────────────────────────────────────────────────────────
    # İşaretleme turu. 1 görürse yanına x koyar, 0 görürse q'ya geçer.
    # Turing s. 234: "o | 1 → R, Px, L, L, L | o"
    #                "o | 0 →                | q"
    ('o', '1'): (
        [('R', None),                       # Sağa git (E-karesine)
         ('P', 'x'),                        # x yaz (sayaç işareti)
         ('L', None), ('L', None),          # İki sola dön (F-karesine)
         ('L', None)],                      # Bir sola daha
        'o'
    ),
    ('o', '0'): ([], 'q'),                  # 0 gör, hiçbir şey yapma, q'ya geç
    ('o', 'a'): ([('R', None), ('R', None)], 'o'),  # a gör, atla

    # ── q durumu ─────────────────────────────────────────────────────────
    # Bantın sonuna git. 0 ya da 1 görürse ilerlemeye devam et.
    # Boş kare görünce dur — bant sonu bulundu.
    # Turing s. 234: "q | 0 veya 1 → R, R | q"
    #                "q | Boş     → P1, L | p"
    ('q', '0'): ([('R', None), ('R', None)], 'q'),
    ('q', '1'): ([('R', None), ('R', None)], 'q'),
    ('q', '_'): ([('P', '1'), ('L', None)], 'p'),   # Sona ulaştı, 1 yaz, geri dön

    # ── p durumu ─────────────────────────────────────────────────────────
    # Geri dön ve x'leri sil. Her x için tekrar sona gidip bir 1 daha yazar.
    # a görürse tur bitti — f durumuna geç.
    # Turing s. 234: "p | x    → E, R  | q"
    #                "p | a    → R     | f"
    #                "p | Boş  → L, L  | p"
    ('p', 'x'): ([('E', None), ('R', None)], 'q'),  # x sil, tekrar sona git
    ('p', 'a'): ([('R', None)], 'f'),               # a gör, tur bitti
    ('p', '0'): ([('L', None), ('L', None)], 'p'),  # 0 gör, sola dön
    ('p', '1'): ([('L', None), ('L', None)], 'p'),  # 1 gör, sola dön
    ('p', '_'): ([('L', None), ('L', None)], 'p'),  # Boş gör, sola dön

    # ── f durumu ─────────────────────────────────────────────────────────
    # Bantın sonuna git ve yeni bir 0 yaz. Yeni tur başlıyor.
    # Turing s. 234: "f | Herhangi → R, R | f"
    #                "f | Boş      → P0, L, L | o"
    ('f', '0'): ([('R', None), ('R', None)], 'f'),
    ('f', '1'): ([('R', None), ('R', None)], 'f'),
    ('f', 'a'): ([('R', None), ('R', None)], 'f'),
    ('f', '_'): (
        [('P', '0'), ('L', None), ('L', None)],     # 0 yaz, iki sola dön
        'o'                                          # Yeni turu başlat
    ),
}


# ─────────────────────────────────────────────
# Çalıştır
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Turing (1936) §3 Örnek II — 001011011101111... Makinesi")
    print("=" * 60)
    print()

    tape, history = run_machine(
        transition_table=transition_table,
        initial_state='b',
        max_steps=500
    )

    # Asıl çıktıyı göster
    output = extract_output(tape)
    print(f"Üretilen dizi ({len(output)} rakam):")
    print(" ".join(output[:30]))
    print()

    # Deseni doğrula
    print("Desen kontrolü (0'lardan sonra gelen 1'lerin sayısı):")
    groups = []
    count = 0
    for bit in output:
        if bit == '1':
            count += 1
        else:
            groups.append(count)
            count = 0
    groups.append(count)

    for i, g in enumerate(groups[:8]):
        print(f"  Grup {i}: {'0' + ' 1'*g if g > 0 else '0'}")

    print()

    # İlk 15 adımın tam konfigürasyonlarını göster
    # Turing §3 s. 235'te tam konfigürasyonu şöyle tanımlar:
    # "taradığı karenin numarası + banttaki tüm semboller + m-konfigürasyon"
    print("İlk 15 adımın tam konfigürasyonları:")
    print(f"{'Adım':>5}  {'Durum':>6}  {'Bant (görünür pencere)'}")
    print("-" * 55)
    for record in history[:15]:
        print(f"{record['step']:>5}  {record['state']:>6}  {record['tape_snapshot']}")

    print()
    print("─" * 60)
    print("Not: x işaretleri geçici sayaç değerleri.")
    print("     a işaretleri başlangıç sınırı.")
    print("     Bant hem çıktı hem bellek olarak kullanılıyor.")
    print("     Bu fikir Von Neumann mimarisinin (1945) öncülüdür.")
