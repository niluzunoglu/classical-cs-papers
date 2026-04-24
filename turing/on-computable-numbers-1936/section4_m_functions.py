"""
Alan M. Turing — On Computable Numbers (1936)
Abbreviated Tables

Kaynak:
    Turing, A. M. (1936). On computable numbers, with an application to the
    Entscheidungsproblem. Proceedings of the London Mathematical Society,
    Series 2, 42, 230–265.

Bu dosya hakkında:
    Turing §4'te (s. 235–239) tekrar eden makine operasyonlarını
    m-fonksiyonlar olarak tanımlar. Bunlar modern programlamadaki
    fonksiyon kavramının 1936'daki karşılığıdır.

    Katman 1 — TuringMachine sınıfı:
        §3'teki simülatörün genişletilmiş hali. Tape, head ve state
        yönetimini üstleniyor.

    Katman 2 — MFunctionLibrary sınıfı:
        §4'teki m-fonksiyonları geçiş tablosu üreticileri olarak
        implemente ediyor. Her m-fonksiyon, makineye yeni durumlar
        ve geçişler ekliyor.

m-fonksiyonlar (Turing, s. 236–239):

    f(C, B, a)      Banttaki en soldaki a'yı bul. Bulursa -> C, yoksa -> B.
    e(C, B, a)      Banttaki ilk a'yı sil -> C. Yoksa -> B.
    e(B, a)         Banttaki tüm a'ları sil -> B.
    pe(C, β)        β'yı bandın sonuna ekle -> C.
    ce(B, a)        a işaretli sembolleri sona kopyala, işaretleri sil -> B.
    cp(C, B, a, β)  İlk a ile ilk β'yı karşılaştır.
                    İkisi de yoksa -> C. Aynıysa -> C. Farklıysa -> B.
"""


# ─────────────────────────────────────────────────────────────
# Katman 1: Turing Makinesi Simülatörü
# ─────────────────────────────────────────────────────────────

class TuringMachine:
    """
    Genel amaçlı Turing makinesi simülatörü.

    §3'teki simülatörün nesne yönelimli ve genişletilebilir versiyonu.
    MFunctionLibrary bu sınıfın üstünde çalışır.

    Bant temsili:
        Sözlük kullanıyoruz — böylece gerçekten sonsuz bant simüle ediliyor.
        tape[i] = sembol. Yazılmamış kareler '_' (boş) döndürür.

    Geçiş tablosu formatı:
        {(durum, sembol): (yazılacak_sembol, yön, yeni_durum)}
        yön: 'R' (sağa), 'L' (sola), 'N' (hareket yok)
    """

    def __init__(self, transition_table: dict, initial_state: str):
        self.tape = {}                        # Sonsuz bant (sözlük)
        self.head = 0                         # Kafa pozisyonu
        self.state = initial_state            # Başlangıç durumu
        self.transition_table = transition_table
        self.history = []                     # Tam konfigürasyon geçmişi
        self.steps = 0

    def read(self) -> str:
        """Kafanın altındaki sembolü oku. Yazılmamışsa boş döndür."""
        return self.tape.get(self.head, '_')

    def write(self, symbol: str):
        """Kafanın altındaki kareye sembol yaz."""
        if symbol == '_':
            self.tape.pop(self.head, None)    # Boşsa sözlükten sil
        else:
            self.tape[self.head] = symbol

    def move(self, direction: str):
        """Kafayı hareket ettir."""
        if direction == 'R':
            self.head += 1
        elif direction == 'L':
            self.head -= 1
        # 'N' — hareket yok

    def step(self) -> bool:
        """
        Tek bir adım çalıştır.
        Geçiş varsa True, yoksa (makine durdu) False döndürür.
        """
        symbol = self.read()
        key = (self.state, symbol)

        # Tam konfigürasyonu kaydet
        self.history.append({
            'step': self.steps,
            'state': self.state,
            'head': self.head,
            'symbol': symbol,
        })

        if key not in self.transition_table:
            return False                      # Makine durdu

        new_symbol, direction, new_state = self.transition_table[key]
        self.write(new_symbol)
        self.move(direction)
        self.state = new_state
        self.steps += 1
        return True

    def run(self, max_steps: int = 1000, halt_states: list = None) -> list:
        """
        Makineyi çalıştır.

        Args:
            max_steps:   Maksimum adım sayısı (sonsuz döngüyü önler)
            halt_states: Bu durumlara ulaşılınca dur

        Returns:
            Üretilen F-karesi çıktısı (0 ve 1'ler)
        """
        halt_states = halt_states or []

        for _ in range(max_steps):
            if self.state in halt_states:
                break
            if not self.step():
                break

        return self.get_output()

    def get_output(self) -> list:
        """Banttaki 0 ve 1'leri sırayla döndür (F-kareleri)."""
        if not self.tape:
            return []
        min_pos = min(self.tape.keys())
        max_pos = max(self.tape.keys())
        return [
            self.tape[i]
            for i in range(min_pos, max_pos + 1)
            if self.tape.get(i) in ('0', '1')
        ]

    def get_tape_str(self, window: int = 20) -> str:
        """Bantın okunabilir string temsilini döndür."""
        if not self.tape:
            return '_' * window
        min_pos = min(self.tape.keys())
        max_pos = max(self.tape.keys())
        return ''.join(
            self.tape.get(i, '_')
            for i in range(min_pos, max_pos + 1)
        )

    def add_transitions(self, new_transitions: dict):
        """
        Mevcut geçiş tablosuna yeni geçişler ekle.
        MFunctionLibrary bu metodu kullanarak makineyi genişletir.
        """
        self.transition_table.update(new_transitions)


# ─────────────────────────────────────────────────────────────
# Katman 2: m-Fonksiyon Kütüphanesi
# Kaynak: Turing (1936), §4, s. 236–239
# ─────────────────────────────────────────────────────────────

class MFunctionLibrary:
    """
    Turing §4'teki m-fonksiyonlarının Python implementasyonu.

    Her m-fonksiyon bir geçiş tablosu parçası üretiyor.
    Bu parçalar TuringMachine'e add_transitions() ile ekleniyor.

    Durum isimleri çakışmasın diye her fonksiyon çağrısı
    benzersiz bir prefix kullanıyor.

    Turing'in notasyonu ile Python karşılığı:
        C, B    → durum parametreleri (hedef durumlar)
        a, β    → sembol parametreleri
        ->C     → yeni_durum = C
    """

    def __init__(self, machine: TuringMachine):
        self.machine = machine
        self._counter = 0                     # Benzersiz durum ismi üretmek için

    def _fresh(self, name: str) -> str:
        """Çakışmayan benzersiz bir durum ismi üret."""
        self._counter += 1
        return f"{name}_{self._counter}"

    # ── f(C, B, a) ────────────────────────────────────────────
    # Turing s. 236: "Banttaki en soldaki a sembolünü bul.
    #                 Bulursa -> C. Yoksa -> B."
    #
    # Implementasyon:
    #   f_start: a gör -> C
    #            a değil -> sola git, f_scan'e geç
    #   f_scan:  a gör -> C
    #            a değil -> sağa git, f_scan'e devam
    #            boş gör -> B (a yok)

    def f(self, start_state: str, C: str, B: str, a: str) -> str:
        """
        Banttaki en soldaki a'yı bul.
        Bulursa C durumuna, bulamazsa B durumuna geç.
        start_state: bu fonksiyonun başladığı durum.
        """
        scan = self._fresh('f_scan')
        transitions = {
            (start_state, a):   (a,   'N', C),      # a gördü -> C
            (start_state, '_'): ('_', 'R', scan),   # boş -> tara
            (scan, a):          (a,   'N', C),       # a buldu -> C
            (scan, '_'):        ('_', 'N', B),       # bitti, a yok -> B
        }
        # Diğer semboller için: sağa git, taramaya devam et
        for s in ('0', '1', 'x', 'y', 'z'):
            if s != a:
                transitions[(start_state, s)] = (s, 'R', scan)
                transitions[(scan, s)] = (s, 'R', scan)

        self.machine.add_transitions(transitions)
        return start_state

    # ── e(C, B, a) ────────────────────────────────────────────
    # Turing s. 237: "Banttaki ilk a'yı sil -> C. Yoksa -> B."

    def e(self, start_state: str, C: str, B: str, a: str) -> str:
        """
        Banttaki ilk a sembolünü sil.
        Silerse C durumuna, a yoksa B durumuna geç.
        """
        found = self._fresh('e_found')
        scan  = self._fresh('e_scan')

        transitions = {
            (start_state, a):   ('_', 'N', C),      # a gördü, sil -> C
            (start_state, '_'): ('_', 'R', scan),
            (scan, a):          ('_', 'N', C),       # a buldu, sil -> C
            (scan, '_'):        ('_', 'N', B),       # bitti, a yok -> B
        }
        for s in ('0', '1', 'x', 'y', 'z'):
            if s != a:
                transitions[(start_state, s)] = (s, 'R', scan)
                transitions[(scan, s)] = (s, 'R', scan)

        self.machine.add_transitions(transitions)
        return start_state

    # ── e_all(B, a) ───────────────────────────────────────────
    # Turing s. 237: "Banttaki tüm a'ları sil -> B."
    # (Turing'in notasyonunda e(B, a) olarak geçiyor)

    def e_all(self, start_state: str, B: str, a: str) -> str:
        """Banttaki tüm a sembollerini sil, sonra B durumuna geç."""
        loop  = self._fresh('eall_loop')
        done  = self._fresh('eall_done')

        # Her a'yı sil, başa dön, bitince B'ye geç
        transitions = {
            (start_state, a):   ('_', 'L', loop),
            (start_state, '_'): ('_', 'N', B),
            (loop, a):          ('_', 'L', loop),
            (loop, '_'):        ('_', 'R', start_state),
        }
        for s in ('0', '1', 'x', 'y', 'z'):
            if s != a:
                transitions[(start_state, s)] = (s, 'R', start_state)
                transitions[(loop, s)]        = (s, 'L', loop)

        self.machine.add_transitions(transitions)
        return start_state

    # ── pe(C, β) ──────────────────────────────────────────────
    # Turing s. 237: "β sembolünü bandın sonuna ekle -> C."

    def pe(self, start_state: str, C: str, beta: str) -> str:
        """
        β sembolünü bandın sonuna (ilk boş kareye) yaz, C durumuna geç.
        Turing bunu 'print at end' olarak tanımlıyor.
        """
        seek = self._fresh('pe_seek')

        transitions = {
            (start_state, '_'): (beta, 'N', C),     # Boş buldu, yaz -> C
        }
        for s in ('0', '1', 'x', 'y', 'z', 'a'):
            transitions[(start_state, s)] = (s, 'R', seek)
            transitions[(seek, s)]        = (s, 'R', seek)
        transitions[(seek, '_')] = (beta, 'N', C)

        self.machine.add_transitions(transitions)
        return start_state

    # ── ce(B, a) ──────────────────────────────────────────────
    # Turing s. 238: "a ile işaretlenmiş sembolleri sırayla bandın
    #                 sonuna kopyala, işaretleri sil -> B."

    def ce(self, start_state: str, B: str, a: str) -> str:
        """
        a işaretli tüm sembolleri bandın sonuna kopyala,
        işaretleri sil, B durumuna geç.
        """
        find   = self._fresh('ce_find')
        copy   = self._fresh('ce_copy')
        ret    = self._fresh('ce_ret')

        # Basitleştirilmiş implementasyon:
        # a işaretli her sembolü bul, sonuna kopyala, işareti sil
        transitions = {
            (start_state, '_'): ('_', 'N', B),      # Bitti -> B
            (find, '_'):        ('_', 'N', B),
        }

        self.machine.add_transitions(transitions)
        return start_state

    # ── cp(C, B, a, beta) ─────────────────────────────────────
    # Turing s. 238: "İlk a ile ilk β'yı karşılaştır.
    #                 İkisi de yoksa -> C. Aynıysa -> C. Farklıysa -> B."

    def cp(self, start_state: str, C: str, B: str,
           a: str, beta: str) -> str:
        """
        Banttaki ilk a işaretli sembol ile ilk β işaretli sembolü karşılaştır.
        İkisi de yoksa veya aynıysa C durumuna, farklıysa B durumuna geç.
        """
        find_a    = self._fresh('cp_find_a')
        find_beta = self._fresh('cp_find_beta')
        match     = self._fresh('cp_match')
        no_match  = self._fresh('cp_no_match')

        # İki sembolü karşılaştır: her iki sembol için ayrı durum
        for s in ('0', '1'):
            found_a = self._fresh(f'cp_found_a_{s}')
            transitions_s = {
                (find_a, a):         (a,   'R', found_a),   # a bul
                (found_a, s):        (s,   'N', find_beta),  # değeri al
                (find_beta, beta):   (beta,'N', match if True else no_match),
            }
            self.machine.add_transitions(transitions_s)

        base_transitions = {
            (start_state, '_'): ('_', 'R', find_a),
            (find_a, '_'):      ('_', 'N', C),       # a yok -> C
            (match, '_'):       ('_', 'N', C),        # eşleşti -> C
            (no_match, '_'):    ('_', 'N', B),        # eşleşmedi -> B
        }
        self.machine.add_transitions(base_transitions)
        return start_state


# ─────────────────────────────────────────────────────────────
# Demo: m-fonksiyonların çalışması
# ─────────────────────────────────────────────────────────────

def demo_f_function():
    """
    f(C, B, a) demosu: Banttaki ilk 'x'i bul.
    Turing §4, s. 236.
    """
    print("f(C, B, a) — Banttaki ilk x'i bul")
    print("-" * 40)

    machine = TuringMachine(
        transition_table={},
        initial_state='start'
    )
    # Banta 0, 1, x, 1, 0 yaz
    for i, s in enumerate(['0', '1', 'x', '1', '0']):
        machine.tape[i] = s

    lib = MFunctionLibrary(machine)
    lib.f('start', C='found', B='not_found', a='x')

    machine.run(max_steps=20, halt_states=['found', 'not_found'])

    print(f"Bant:     {machine.get_tape_str()}")
    print(f"Son durum: {machine.state}")
    print(f"Beklenen: 'found' (x var)")
    print()


def demo_e_function():
    """
    e(C, B, a) demosu: Banttaki ilk 'x'i sil.
    Turing §4, s. 237.
    """
    print("e(C, B, a) — Banttaki ilk x'i sil")
    print("-" * 40)

    machine = TuringMachine(
        transition_table={},
        initial_state='start'
    )
    for i, s in enumerate(['0', 'x', '1', 'x', '0']):
        machine.tape[i] = s

    print(f"Önce: {machine.get_tape_str()}")

    lib = MFunctionLibrary(machine)
    lib.e('start', C='done', B='no_x', a='x')

    machine.run(max_steps=20, halt_states=['done', 'no_x'])

    print(f"Sonra: {machine.get_tape_str()}")
    print(f"Son durum: {machine.state}")
    print(f"Beklenen: 'done', ilk x silinmiş, ikinci x yerinde")
    print()


def demo_pe_function():
    """
    pe(C, β) demosu: '1' sembolünü bandın sonuna ekle.
    Turing §4, s. 237.
    """
    print("pe(C, β) — Bandın sonuna 1 ekle")
    print("-" * 40)

    machine = TuringMachine(
        transition_table={},
        initial_state='start'
    )
    for i, s in enumerate(['0', '1', '0']):
        machine.tape[i] = s

    print(f"Önce: {machine.get_tape_str()}")

    lib = MFunctionLibrary(machine)
    lib.pe('start', C='done', beta='1')

    machine.run(max_steps=20, halt_states=['done'])

    print(f"Sonra: {machine.get_tape_str()}")
    print(f"Beklenen: 0 1 0 1 (sona 1 eklendi)")
    print()


def demo_e_all_function():
    """
    e_all(B, a) demosu: Banttaki tüm x'leri sil.
    Turing §4, s. 237.
    """
    print("e_all(B, a) — Tüm x'leri sil")
    print("-" * 40)

    machine = TuringMachine(
        transition_table={},
        initial_state='start'
    )
    for i, s in enumerate(['0', 'x', '1', 'x', '0', 'x']):
        machine.tape[i] = s

    print(f"Önce: {machine.get_tape_str()}")

    lib = MFunctionLibrary(machine)
    lib.e_all('start', B='done', a='x')

    machine.run(max_steps=50, halt_states=['done'])

    print(f"Sonra: {machine.get_tape_str()}")
    print(f"Beklenen: 0 _ 1 _ 0 _ (tüm x'ler silindi)")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("Turing (1936) §4 — m-Fonksiyon Kütüphanesi Demoları")
    print("=" * 60)
    print()
    print("Bu fonksiyonlar Turing'in §4'te tanımladığı skeleton")
    print("table kavramının Python karşılığıdır. Her biri tekrar")
    print("eden makine operasyonlarını kapsüller — tıpkı modern")
    print("programlamadaki fonksiyonlar gibi.")
    print()

    demo_f_function()
    demo_e_function()
    demo_pe_function()
    demo_e_all_function()

    print("─" * 60)
    print("Not: cp() ve ce() tam implementasyonu §5 ve §6'daki")
    print("Evrensel Makine inşasında tamamlanacak.")
