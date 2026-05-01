"""
Alan M. Turing — On Computable Numbers (1936)
Bölüm §7: Detailed Description of the Universal Machine

Kaynak:
    Turing, A. M. (1936). On computable numbers, with an application to the
    Entscheidungsproblem. Proceedings of the London Mathematical Society,
    Series 2, 42, 230-265.

Bu dosya hakkında:
    Turing §7'de (s. 243-246) U'nun tam geçiş tablosunu verir.
    Bu bölüm makalenin en teknik kısmıdır.

    U bir yorumlayıcıdır (interpreter):
        - Bantın başındaki S.D'yi okur
        - Hedef makinenin konfigürasyonunu takip eder
        - Her adımda doğru talimatı bulur ve uygular
        - Yeni konfigürasyonu banta yazar

    Bant düzeni (Turing s. 243):
        [ a ][ a ][ S.D ][ :: ][ CC0 ][ CC1 ][ CC2 ]...

        a    → başlangıç işaretleyicisi
        S.D  → hedef makinenin Standard Description'ı
        ::   → S.D sonu işaretleyicisi
        CC_n → n'inci tam konfigürasyon

    m-konfigürasyonlar (Turing s. 244-246):
        b    → başlangıç, banta :DA yazar
        anf  → son tam konfigürasyonu y ile işaretle
        fom  → ilgili talimatı S.D'de bul
        sim  → konfigürasyonu talimatla karşılaştır
        mf   → talimatı uygula, yeni konfigürasyonu yaz
        inst → 0 veya 1 yazdırılacaksa çıktıya ekle

    Bu dosya §6'daki UniversalTuringMachine'i genişleterek
    Turing'in §7'de tarif ettiği iç mekanizmayı şeffaf hale getirir.
    Her m-konfigürasyon adımı loglanır ve görselleştirilir.
"""

from section4_mfunctions import TuringMachine
from section5_enumeration import (
    TuringMachineEncoder,
    decode_description_number,
)
from section6_universal_machine import SDParser


# ─────────────────────────────────────────────────────────────
# Tam Konfigürasyon Temsili
# Kaynak: Turing (1936), §7, s. 242-243
# ─────────────────────────────────────────────────────────────

class CompleteConfiguration:
    """
    Hedef makinenin tek bir tam konfigürasyonu.

    Turing §3'te tam konfigürasyonu şöyle tanımlar:
    "taradığı karenin numarası + banttaki tüm semboller + m-konfigürasyon"

    §7'de U bu bilgiyi S.D formatında bantına yazar:
        D A...A  → m-konfigürasyon
        D C...C  → her sembol
    """

    def __init__(self, state: str, tape_symbols: list, head_pos: int):
        self.state = state
        self.tape_symbols = tape_symbols    # Banttaki semboller (soldan sağa)
        self.head_pos = head_pos            # Kafanın pozisyonu

    def to_sd_format(self) -> str:
        """
        Tam konfigürasyonu S.D formatında string olarak döndür.
        Turing §7, s. 242: CC_n gösterimi.

        Format: semboller + [durum işaretleyici] + semboller
        Kafa pozisyonundaki sembolün soluna durum yazılır.
        """
        result = []
        for i, sym in enumerate(self.tape_symbols):
            if i == self.head_pos:
                result.append(f"[{self.state}]")
            result.append(sym if sym != '_' else ' ')
        return ''.join(result)

    def __repr__(self):
        return f"CC(state={self.state}, head={self.head_pos}, tape={self.tape_symbols})"


# ─────────────────────────────────────────────────────────────
# U'nun İç m-konfigürasyonları
# Kaynak: Turing (1936), §7, s. 244-246
# ─────────────────────────────────────────────────────────────

class UInternalState:
    """
    U'nun iç m-konfigürasyonlarını temsil eder.

    Turing §7'de U'nun şu m-konfigürasyonlarını tanımlar:
        b, anf, fom, sim, mf, inst

    Bu sınıf her m-konfigürasyonun ne yaptığını
    adım adım simüle eder ve loglar.
    """

    # m-konfigürasyonların açıklamaları (Turing s. 244-246)
    STATE_DESCRIPTIONS = {
        'b':    "Başlangıç: banta :DA yaz, anf'e geç",
        'anf':  "Son tam konfigürasyonu y ile işaretle, fom'a geç",
        'fom':  "S.D'de işaretlenmemiş son noktalı virgülü bul, z ile işaretle",
        'sim':  "x ile işaretli konfigürasyonu y ile işaretli olanla karşılaştır",
        'mf':   "Son konfigürasyonu dört bölüme ayır, talimatı uygula",
        'inst': "P0 veya P1 varsa çıktıya 0: veya 1: yaz",
        'ov':   "Tamamlandı, anf'e dön",
    }

    def __init__(self):
        self.current = 'b'
        self.log = []

    def transition(self, new_state: str, reason: str = ""):
        """m-konfigürasyon geçişini logla."""
        entry = {
            'from': self.current,
            'to': new_state,
            'reason': reason,
            'description': self.STATE_DESCRIPTIONS.get(new_state, ""),
        }
        self.log.append(entry)
        self.current = new_state

    def describe_current(self) -> str:
        return self.STATE_DESCRIPTIONS.get(self.current, "Bilinmiyor")


# ─────────────────────────────────────────────────────────────
# Detaylı Universal Turing Machine
# Kaynak: Turing (1936), §7, s. 243-246
# ─────────────────────────────────────────────────────────────

class DetailedUniversalTuringMachine:
    """
    §7'nin detaylı açıklamasına sadık U implementasyonu.

    §6'daki UniversalTuringMachine'den farkı:
        - Her m-konfigürasyon adımı görünür
        - Bantın tam durumu her adımda loglanır
        - U'nun iç mekanizması şeffaf

    U'nun çalışma döngüsü (Turing §7):

        b → anf → fom → sim → mf → inst → ov → anf → ...

        b:    Bantı hazırla
        anf:  Son CC'yi bul, işaretle
        fom:  S.D'de ilgili talimatı bul
        sim:  Konfigürasyonu talimatla eşleştir
        mf:   Talimatı uygula
        inst: Çıktı üret (0 veya 1)
        ov:   Yeni CC'yi yaz, başa dön
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.parser = SDParser()
        self.u_state = UInternalState()
        self.configurations = []     # Tüm tam konfigürasyonlar
        self.output_sequence = []    # Üretilen 0/1 dizisi
        self.step_log = []           # Her adımın detaylı logu

    def _log(self, message: str, level: int = 0):
        """Simülasyon logu."""
        if self.verbose:
            indent = "  " * level
            print(f"{indent}{message}")

    def _build_initial_tape(self, sd: str) -> dict:
        """
        U'nun başlangıç bantını oluştur.

        Turing §7, s. 243:
        "When U is ready to start work the tape running through it
        bears on it the symbol a on an F-square and again a on the
        next E-square; after this, on F-squares only, comes the S.D
        of the machine followed by a double colon '::'."

        Bant düzeni:
            Pos 0: 'a'  (başlangıç işaretleyicisi)
            Pos 1: 'a'  (ikinci işaretleyici)
            Pos 2..n: S.D karakterleri
            Pos n+1: '::'
        """
        tape = {}
        tape[0] = 'a'
        tape[1] = 'a'

        for i, ch in enumerate(sd):
            tape[i + 2] = ch

        tape[len(sd) + 2] = ':'     # :: işaretleyicisi
        tape[len(sd) + 3] = ':'

        return tape

    def _tape_to_str(self, tape: dict, start: int = 0, end: int = None) -> str:
        """Bantı okunabilir stringe çevir."""
        if not tape:
            return ""
        max_pos = max(tape.keys())
        end = end or max_pos + 1
        return ''.join(tape.get(i, '_') for i in range(start, end))

    def simulate(
        self,
        sd: str,
        max_cycles: int = 50,
    ) -> list:
        """
        Hedef makineyi simüle et.

        U'nun çalışma mantığı:
            Her döngüde hedef makinenin bir adımını simüle eder.
            Bunu yaparken S.D'yi referans alır ve
            tam konfigürasyonları banta yazar.

        Args:
            sd:         Hedef makinenin Standard Description'ı
            max_cycles: Maksimum simülasyon döngüsü

        Returns:
            Üretilen 0/1 dizisi
        """
        # 1. Hedef makineyi ayrıştır
        transition_table = self.parser.parse(sd)
        if not transition_table:
            raise ValueError(f"Geçersiz S.D: {sd}")

        # 2. Hedef makineyi başlat
        target = TuringMachine(
            transition_table=transition_table,
            initial_state='q1'
        )

        # 3. U'nun bantını hazırla
        u_tape = self._build_initial_tape(sd)

        self._log("=" * 60)
        self._log("U — Detaylı Universal Turing Machine Simülasyonu")
        self._log("Kaynak: Turing (1936), §7, s. 243-246")
        self._log("=" * 60)
        self._log("")
        self._log(f"Hedef makine S.D'si: {sd[:50]}{'...' if len(sd) > 50 else ''}")
        self._log("")
        self._log("Bantın başlangıç durumu:")
        self._log(f"  {self._tape_to_str(u_tape)}")
        self._log("")

        # 4. Ana simülasyon döngüsü
        # U'nun m-konfigürasyonlarını taklit ediyoruz:
        # b → anf → fom → sim → mf → inst → ov → anf → ...

        for cycle in range(max_cycles):
            self._log(f"Döngü {cycle + 1}:", level=0)

            # ── anf: Son tam konfigürasyonu bul ──────────────
            self.u_state.transition('anf', "Son CC'yi işaretle")
            self._log(
                f"  [anf] {self.u_state.describe_current()}",
                level=1
            )

            state  = target.state
            symbol = target.read()
            key    = (state, symbol)

            # Tam konfigürasyonu kaydet
            tape_symbols = [
                target.tape.get(i, '_')
                for i in range(
                    min(target.tape.keys(), default=0),
                    max(target.tape.keys(), default=0) + 1
                )
            ] if target.tape else ['_']

            cc = CompleteConfiguration(
                state=state,
                tape_symbols=tape_symbols,
                head_pos=target.head - min(target.tape.keys(), default=0)
            )
            self.configurations.append(cc)

            self._log(
                f"  [CC_{cycle}] {cc.to_sd_format()}",
                level=1
            )

            # ── fom: İlgili talimatı S.D'de bul ─────────────
            self.u_state.transition('fom', f"({state}, {symbol!r}) için talimat ara")
            self._log(
                f"  [fom] {self.u_state.describe_current()}",
                level=1
            )

            if key not in transition_table:
                self._log(
                    f"  [fom] Talimat bulunamadı — makine durdu.",
                    level=1
                )
                break

            write_sym, direction, next_state = transition_table[key]

            self._log(
                f"  [fom] Talimat bulundu: "
                f"({state}, {symbol!r}) → "
                f"yaz={write_sym!r}, yön={direction}, "
                f"sonraki={next_state}",
                level=1
            )

            # ── sim: Konfigürasyonu talimatla eşleştir ───────
            self.u_state.transition('sim', "Konfigürasyonu doğrula")
            self._log(
                f"  [sim] {self.u_state.describe_current()}",
                level=1
            )

            # ── mf: Talimatı uygula ───────────────────────────
            self.u_state.transition('mf', "Talimatı uygula")
            self._log(
                f"  [mf]  {self.u_state.describe_current()}",
                level=1
            )

            target.step()

            # ── inst: Çıktı üret ──────────────────────────────
            self.u_state.transition('inst', "Çıktı kontrol")

            if write_sym in ('0', '1'):
                self.output_sequence.append(write_sym)
                self._log(
                    f"  [inst] Çıktı üretildi: {write_sym}",
                    level=1
                )

            # ── ov: Tamamlandı ────────────────────────────────
            self.u_state.transition('ov', "Döngü tamamlandı")

            # Adım logu
            self.step_log.append({
                'cycle':       cycle,
                'cc':          cc,
                'instruction': (state, symbol, write_sym, direction, next_state),
                'output':      write_sym if write_sym in ('0', '1') else None,
            })

            self._log("")

        return self.output_sequence

    def simulate_from_dn(self, dn: str, max_cycles: int = 50) -> list:
        """D.N'den simülasyon başlat."""
        decoded = decode_description_number(dn)
        self._log(f"D.N → S.D: {decoded['sd'][:50]}...")
        self._log("")
        return self.simulate(decoded['sd'], max_cycles=max_cycles)

    def print_summary(self):
        """Simülasyon özetini yazdır."""
        print()
        print("=" * 60)
        print("Simülasyon Özeti")
        print("=" * 60)
        print(f"Toplam döngü     : {len(self.step_log)}")
        print(f"Üretilen çıktı   : {' '.join(self.output_sequence)}")
        print(f"Tam konfigürasyon sayısı: {len(self.configurations)}")
        print()
        print("m-konfigürasyon geçiş logu (ilk 10):")
        print(f"  {'Kimden':>6} → {'Kime':>6}  Neden")
        print(f"  {'-'*6}   {'-'*6}  {'-'*30}")
        for entry in self.u_state.log[:10]:
            print(
                f"  {entry['from']:>6} → {entry['to']:>6}  "
                f"{entry['reason']}"
            )

    def print_configurations(self):
        """Tüm tam konfigürasyonları yazdır."""
        print()
        print("Tam Konfigürasyonlar (Turing §7, s. 242-243):")
        print("-" * 55)
        for i, cc in enumerate(self.configurations):
            print(f"  CC_{i}: {cc.to_sd_format()}")


# ─────────────────────────────────────────────────────────────
# Demo
# ─────────────────────────────────────────────────────────────

def demo_section7_machine1():
    """
    U §3 Makine I'i simüle ediyor — §7'nin tam mekanizmasıyla.
    Turing §7, s. 243-246.
    """
    print("Demo: §7 Detaylı U — §3 Makine I (010101...)")
    print()

    states  = ['b', 'c', 'e', 'f']
    symbols = ['_', '0', '1']
    encoder = TuringMachineEncoder(states, symbols)

    transitions = [
        ('b', '_', '0', 'R', 'c'),
        ('c', '_', '_', 'R', 'e'),
        ('e', '_', '1', 'R', 'f'),
        ('f', '_', '_', 'R', 'b'),
    ]

    result = encoder.encode_machine(transitions)
    sd = result['sd']

    utm = DetailedUniversalTuringMachine(verbose=True)
    output = utm.simulate(sd, max_cycles=12)

    utm.print_summary()
    utm.print_configurations()


def demo_section7_silent():
    """
    Sessiz mod: çıktıya odaklan.
    """
    print()
    print("Demo: §7 Detaylı U — Sessiz Mod (çıktıya odaklan)")
    print("-" * 55)

    states  = ['b', 'c', 'e', 'f']
    symbols = ['_', '0', '1']
    encoder = TuringMachineEncoder(states, symbols)

    transitions = [
        ('b', '_', '0', 'R', 'c'),
        ('c', '_', '_', 'R', 'e'),
        ('e', '_', '1', 'R', 'f'),
        ('f', '_', '_', 'R', 'b'),
    ]

    result = encoder.encode_machine(transitions)

    utm = DetailedUniversalTuringMachine(verbose=False)
    output = utm.simulate(result['sd'], max_cycles=20)

    print(f"Üretilen dizi: {' '.join(output)}")
    print(f"Beklenen     : 0 1 0 1 0 1 0 1 0 1 ...")
    print()

    print("m-konfigürasyon döngüsü (Turing §7, s. 244):")
    print()
    seen_states = []
    for entry in utm.u_state.log[:14]:
        if entry['to'] not in seen_states:
            seen_states.append(entry['to'])
            print(f"  {entry['to']:>6} — {entry['description']}")

    print()
    print("Bu döngü: b → anf → fom → sim → mf → inst → ov → anf → ...")
    print("Her turda hedef makinenin bir adımı simüle edilir.")


# ─────────────────────────────────────────────────────────────
# Çalıştır
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Turing (1936) §7 — Detailed Description of U")
    print("=" * 60)
    print()

    demo_section7_machine1()
    demo_section7_silent()

    print()
    print("─" * 60)
    print("Not: §8'de Turing bu U'yu ve §5'teki D.N kodlamasını")
    print("kullanarak Halting Problem'in çözümsüzlüğünü ispat eder.")
    print("Eğer döngüselliği test eden bir D makinesi olsaydı,")
    print("U ile birleştirilerek mantıksal bir çelişki üretilirdi.")
