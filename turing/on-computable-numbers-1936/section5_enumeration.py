"""
Alan M. Turing — On Computable Numbers (1936)
Bölüm §5: Enumeration of Computable Sequences

Kaynak:
    Turing, A. M. (1936). On computable numbers, with an application to the
    Entscheidungsproblem. Proceedings of the London Mathematical Society,
    Series 2, 42, 230-265.

Bu dosya hakkında:
    Turing §5'te (s. 239-241) her Turing makinesinin bir sayıyla
    temsil edilebileceğini gösterir. Bu, hesaplanabilir dizilerin
    sayılabilir (enumerable) olduğunun ispatının temelidir.

    Kodlama iki adımda gerçekleşir:

    Adım 1 — Standard Description (S.D):
        Her talimat q_i S_j S_k L/R/N q_m biçiminde yazılır.
        q_i  → "D" + "A" * i          (örn: q2 → DAA)
        S_j  → "D" + "C" * j          (örn: S1 → DC, boşluk → D)
        Talimatlar noktalı virgülle ayrılır.

    Adım 2 — Description Number (D.N):
        S.D içindeki her harf bir rakamla değiştirilir:
        A→1, C→2, D→3, L→4, R→5, N→6, ;→7

    Turing s. 241'de §3'teki Makine I için şu D.N'yi hesaplar:
        31332531173113353111731113322531111731111335317

    Bu dosya o hesabı yeniden üretir ve doğrular.

Önemli kavramlar:
    Standard Description (S.D): Makinenin sembolik kodlaması
    Description Number (D.N):   Makinenin sayısal kodlaması
    Satisfactory Number:        Döngüsüz bir makinenin D.N'si

Büyük fikir:
    Her makine bir sayıya karşılık gelir.
    Her sayı en fazla bir makineye karşılık gelir.
    Dolayısıyla hesaplanabilir diziler sayılabilir.
    Bu §8'deki Halting Problem ispatının zeminini hazırlar.
"""

from section4_mfunctions import TuringMachine


# ─────────────────────────────────────────────────────────────
# Kodlama Sabitleri
# Kaynak: Turing (1936), §5, s. 240
# ─────────────────────────────────────────────────────────────

# Turing'in harf → rakam dönüşüm tablosu (s. 240)
LETTER_TO_DIGIT = {
    'A': '1',
    'C': '2',
    'D': '3',
    'L': '4',
    'R': '5',
    'N': '6',
    ';': '7',
}

DIGIT_TO_LETTER = {v: k for k, v in LETTER_TO_DIGIT.items()}


# ─────────────────────────────────────────────────────────────
# Standart Form
# Kaynak: Turing (1936), §5, s. 239-240
# ─────────────────────────────────────────────────────────────

def state_to_sd(state_index: int) -> str:
    """
    Durum numarasını S.D gösterimine çevir.
    Turing s. 240: q_i → "D" + "A" * i

    Örnek:
        q1 → DA
        q2 → DAA
        q3 → DAAA
    """
    return 'D' + 'A' * state_index


def symbol_to_sd(symbol_index: int) -> str:
    """
    Sembol numarasını S.D gösterimine çevir.
    Turing s. 240: S_j → "D" + "C" * j

    Turing'in sembol tablosu:
        S0 = boşluk (_) → D
        S1 = 0          → DC
        S2 = 1          → DCC

    Örnek:
        S0 → D
        S1 → DC
        S2 → DCC
    """
    return 'D' + 'C' * symbol_index


def instruction_to_sd(
    q_i: int,
    s_j: int,
    s_k: int,
    direction: str,
    q_m: int
) -> str:
    """
    Tek bir talimatı S.D gösterimine çevir.
    Turing s. 240: q_i S_j S_k L/R/N q_m

    Args:
        q_i:       Başlangıç durumu indeksi
        s_j:       Okunan sembol indeksi
        s_k:       Yazılacak sembol indeksi
        direction: 'L', 'R', veya 'N'
        q_m:       Sonraki durum indeksi

    Örnek:
        q1 S0 S1 R q2 → DA D DC R DAA
    """
    return (
        state_to_sd(q_i) +
        symbol_to_sd(s_j) +
        symbol_to_sd(s_k) +
        direction +
        state_to_sd(q_m)
    )


# ─────────────────────────────────────────────────────────────
# Encoder: Makine → S.D → D.N
# Kaynak: Turing (1936), §5, s. 240-241
# ─────────────────────────────────────────────────────────────

class TuringMachineEncoder:
    """
    Turing makinesini Standard Description (S.D) ve
    Description Number (D.N) olarak kodlar.

    Turing s. 239: "Tüm bu tabloları standart bir forma sokmak
    faydalı olacaktır."

    Kullanım:
        encoder = TuringMachineEncoder(states, symbols)
        sd = encoder.to_standard_description(instructions)
        dn = encoder.to_description_number(sd)
    """

    def __init__(self, states: list, symbols: list):
        """
        Args:
            states:  Durum listesi — ilk eleman başlangıç durumu (q1)
            symbols: Sembol listesi — ['_', '0', '1', ...]
                     '_' her zaman S0 (indeks 0) olmalı
        """
        self.states = states
        self.symbols = symbols

        # İndeks tabloları
        self.state_index  = {s: i + 1 for i, s in enumerate(states)}
        self.symbol_index = {s: i for i, s in enumerate(symbols)}

    def encode_transition(
        self,
        state: str,
        read_symbol: str,
        write_symbol: str,
        direction: str,
        next_state: str
    ) -> str:
        """
        Tek bir geçişi S.D formatına çevir.
        Turing s. 240: N1, N2, N3 formları.
        """
        q_i = self.state_index[state]
        s_j = self.symbol_index[read_symbol]
        s_k = self.symbol_index[write_symbol]
        q_m = self.state_index[next_state]

        return instruction_to_sd(q_i, s_j, s_k, direction, q_m)

    def to_standard_description(self, transitions: list) -> str:
        """
        Tüm geçiş listesini Standard Description'a çevir.
        Talimatlar noktalı virgülle ayrılır.

        Args:
            transitions: [(state, read, write, direction, next_state), ...]

        Returns:
            Standard Description string
        """
        instructions = [
            self.encode_transition(st, rd, wr, dr, nx)
            for st, rd, wr, dr, nx in transitions
        ]
        return ';'.join(instructions)

    def to_description_number(self, sd: str) -> str:
        """
        Standard Description'ı Description Number'a çevir.
        Turing s. 240: A→1, C→2, D→3, L→4, R→5, N→6, ;→7

        Returns:
            Description Number (büyük tam sayı, string olarak)
        """
        return ''.join(LETTER_TO_DIGIT[ch] for ch in sd)

    @staticmethod
    def from_description_number(dn: str) -> str:
        """
        Description Number'ı Standard Description'a çevir.
        Tersine çözümleme (decoding).
        """
        return ''.join(DIGIT_TO_LETTER[ch] for ch in dn)

    def encode_machine(self, transitions: list) -> dict:
        """
        Makineyi tam olarak kodla, tüm gösterimleri döndür.

        Returns:
            {
                'sd': Standard Description,
                'dn': Description Number,
                'instructions': talimat listesi,
            }
        """
        sd = self.to_standard_description(transitions)
        dn = self.to_description_number(sd)

        return {
            'sd': sd,
            'dn': dn,
            'instructions': sd.split(';'),
        }


# ─────────────────────────────────────────────────────────────
# Decoder: D.N → Makine
# ─────────────────────────────────────────────────────────────

def parse_sd_token(token: str) -> tuple:
    """
    Tek bir S.D talimatını ayrıştır.
    Format: D A...A D C...C D C...C L/R/N D A...A

    Returns:
        (q_i, s_j, s_k, direction, q_m) olarak indeksler
    """
    i = 0
    result = []

    while i < len(token):
        if token[i] == 'D':
            i += 1
            count = 0
            marker = None

            while i < len(token) and token[i] in ('A', 'C'):
                marker = token[i]
                count += 1
                i += 1

            result.append((marker, count))

        elif token[i] in ('L', 'R', 'N'):
            result.append(('dir', token[i]))
            i += 1

        else:
            i += 1

    # result formatı: [(A, q_i), (C, s_j), (C, s_k), (dir, d), (A, q_m)]
    q_i = result[0][1] if result[0][0] == 'A' else 0
    s_j = result[1][1] if len(result) > 1 else 0
    s_k = result[2][1] if len(result) > 2 else 0
    direction = result[3][1] if len(result) > 3 else 'N'
    q_m = result[4][1] if len(result) > 4 else 1

    return q_i, s_j, s_k, direction, q_m


def decode_description_number(dn: str) -> dict:
    """
    Description Number'dan makine bilgisini çıkar.

    Args:
        dn: Description Number string

    Returns:
        {
            'sd': Standard Description,
            'transitions': [(q_i, s_j, s_k, dir, q_m), ...]
        }
    """
    sd = TuringMachineEncoder.from_description_number(dn)
    instructions = sd.split(';')
    transitions = [parse_sd_token(inst) for inst in instructions if inst]

    return {
        'sd': sd,
        'transitions': transitions,
    }


# ─────────────────────────────────────────────────────────────
# Doğrulama: §3 Makine I
# Kaynak: Turing (1936), §5, s. 241
# ─────────────────────────────────────────────────────────────

def verify_machine_1():
    """
    §3 Makine I (010101...) için Turing'in s.241'deki
    D.N hesabını yeniden üretir ve doğrular.

    Turing'in verdiği S.D (s. 241):
        DADDCRDAA;DAADDRDAAA;DAAADDCCRDAAAA;DAAAADDRDA

    Turing'in verdiği D.N (s. 241):
        31332531173113353111731113322531111731111335317
    """
    print("§3 Makine I — 010101... Kodlama Doğrulaması")
    print("Kaynak: Turing (1936), §5, s. 241")
    print("-" * 55)

    # Makine I'in standart formu (Turing s. 241)
    # Durum yeniden adlandırma: b→q1, c→q2, e→q3, f→q4
    # Semboller: _=S0, 0=S1, 1=S2
    states  = ['b', 'c', 'e', 'f']
    symbols = ['_', '0', '1']

    encoder = TuringMachineEncoder(states, symbols)

    # Turing s. 241'deki talimatlar
    # q1 S0 S1 R q2 → b gör boş, 0 yaz, sağa git, c'ye geç
    # q2 S0 S0 R q3 → c gör boş, boş yaz, sağa git, e'ye geç
    # q3 S0 S2 R q4 → e gör boş, 1 yaz,  sağa git, f'ye geç
    # q4 S0 S0 R q1 → f gör boş, boş yaz, sağa git, b'ye geç
    transitions = [
        ('b', '_', '0', 'R', 'c'),
        ('c', '_', '_', 'R', 'e'),
        ('e', '_', '1', 'R', 'f'),
        ('f', '_', '_', 'R', 'b'),
    ]

    result = encoder.encode_machine(transitions)

    print(f"Standard Description (S.D):")
    print(f"  {result['sd']}")
    print()
    print(f"Talimatlar:")
    for i, inst in enumerate(result['instructions'], 1):
        print(f"  {i}. {inst}")
    print()
    print(f"Description Number (D.N):")
    print(f"  {result['dn']}")
    print()

    # Turing'in verdiği D.N ile karşılaştır
    turing_dn = "31332531173113353111731113322531111731111335317"
    match = result['dn'] == turing_dn

    print(f"Turing'in D.N'si (s. 241):")
    print(f"  {turing_dn}")
    print()
    print(f"Doğrulama: {'BASARILI' if match else 'HATA'}")
    print()


def verify_decoding():
    """
    D.N → S.D → talimatlar tersine çözümleme doğrulaması.
    """
    print("Tersine Çözümleme (D.N → Makine) Doğrulaması")
    print("-" * 55)

    dn = "31332531173113353111731111335317"

    decoded = decode_description_number(dn)

    print(f"Description Number: {dn}")
    print(f"Standard Description: {decoded['sd']}")
    print(f"Talimatlar:")
    for i, (qi, sj, sk, d, qm) in enumerate(decoded['transitions'], 1):
        print(f"  {i}. q{qi} S{sj} S{sk} {d} q{qm}")
    print()


def show_enumeration():
    """
    Hesaplanabilir dizilerin sayılabilirliğini göster.
    Turing §5: Her makine bir sayıya karşılık gelir,
    dolayısıyla hesaplanabilir diziler sayılabilir.
    """
    print("Hesaplanabilir Dizilerin Sayılabilirliği")
    print("Kaynak: Turing (1936), §5, s. 241")
    print("-" * 55)
    print()
    print("Her Turing makinesi bir D.N'ye karşılık gelir:")
    print()

    machines = [
        {
            'name': '010101... makinesi (§3 Makine I)',
            'dn': '31332531173113353111731113322531111731111335317',
        },
    ]

    for m in machines:
        print(f"  Makine : {m['name']}")
        print(f"  D.N    : {m['dn']}")
        print(f"  (Bu D.N bir tam sayı: {int(m['dn']):,})")
        print()

    print("Sonuç:")
    print("  Her hesaplanabilir dizi → en az bir D.N")
    print("  Her D.N → en fazla bir hesaplanabilir dizi")
    print("  D.N'ler doğal sayıların bir alt kümesi")
    print("  Dolayısıyla hesaplanabilir diziler sayılabilir.")
    print()
    print("  Bu gerçek sayılarla çelişmiyor:")
    print("  Gerçek sayılar sayılamaz (Cantor, 1891)")
    print("  Hesaplanabilir sayılar sayılabilir (Turing, 1936)")
    print("  Yani hesaplanamayan gerçek sayılar var — sonsuz çok.")


# ─────────────────────────────────────────────────────────────
# Çalıştır
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Turing (1936) §5 — Computable Sequences Enumeration")
    print("=" * 60)
    print()

    verify_machine_1()
    verify_decoding()
    show_enumeration()

    print("─" * 60)
    print("Not: §8'de Turing bu sayılabilirliği kullanarak")
    print("Halting Problem'in çözümsüzlüğünü ispat edecek.")
    print("§6'da ise bu D.N'leri girdi olarak alan Evrensel")
    print("Turing Makinesi tanımlanacak.")
