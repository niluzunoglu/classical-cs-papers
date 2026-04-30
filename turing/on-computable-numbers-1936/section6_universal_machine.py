"""
Alan M. Turing — On Computable Numbers (1936)
Bölüm §6: The Universal Computing Machine

Kaynak:
    Turing, A. M. (1936). On computable numbers, with an application to the
    Entscheidungsproblem. Proceedings of the London Mathematical Society,
    Series 2, 42, 230-265.

Bu dosya hakkında:
    Turing §6'da (s. 241-242) tek bir makinenin, doğru girdi
    verildiğinde, herhangi bir hesaplanabilir diziyi üretebileceğini
    gösterir. Bu makineye Universal Computing Machine (U) denir.

    "It is possible to invent a single machine which can be used to
    compute any computable sequence."
    — Turing, s. 241

    U'nun çalışma prensibi:
        1. Bantın başına hedef makinenin S.D'si yazılır
        2. U bu S.D'yi okur ve talimatları yorumlar
        3. Hedef makinenin ürettiği diziyi üretir

    Bu modern bilgisayarların tam karşılığıdır:
        S.D      → program (kaynak kod)
        U        → işlemci (CPU)
        Bant     → bellek (RAM)

    Bu dosyada U'yu Python'da implemente ediyoruz.
    Girdi olarak herhangi bir makinenin S.D'sini alır,
    o makinenin ürettiği diziyi simüle eder.

Mimari:
    UniversalTuringMachine sınıfı:
        - S.D veya D.N girdi olarak alır
        - Hedef makineyi ayrıştırır
        - Adım adım simüle eder
        - Çıktıyı üretir

    Bu, §5'teki Encoder ve §4'teki TuringMachine
    sınıflarıyla birlikte çalışır.
"""

from section4_mfunctions import TuringMachine
from section5_enumeration import (
    TuringMachineEncoder,
    decode_description_number,
    LETTER_TO_DIGIT,
    DIGIT_TO_LETTER,
)


# ─────────────────────────────────────────────────────────────
# S.D Ayrıştırıcı
# Kaynak: Turing (1936), §6, s. 241-242
# ─────────────────────────────────────────────────────────────

class SDParser:
    """
    Standard Description'ı ayrıştırır ve çalıştırılabilir
    geçiş tablosuna çevirir.

    Turing §6'da S.D formatını şöyle tanımlar (s. 243):
        (i)   D + A*i  → m-konfigürasyon (durum)
        (ii)  D + C*j  → okunan sembol
        (iii) D + C*k  → yazılacak sembol
        (iv)  L/R/N    → yön
        (v)   D + A*m  → sonraki m-konfigürasyon
    """

    # Turing'in sembol tablosu (§5, s. 240)
    INDEX_TO_SYMBOL = {0: '_', 1: '0', 2: '1'}
    SYMBOL_TO_INDEX = {'_': 0, '0': 1, '1': 2}

    def parse(self, sd: str) -> dict:
        """
        S.D'yi geçiş tablosuna çevir.

        Args:
            sd: Standard Description string

        Returns:
            {(durum, sembol): (yazılacak, yön, yeni_durum)}
        """
        instructions = [i for i in sd.split(';') if i.strip()]
        transition_table = {}

        for inst in instructions:
            parsed = self._parse_instruction(inst)
            if parsed:
                (q_i, s_j, s_k, direction, q_m) = parsed
                state      = f"q{q_i}"
                read_sym   = self.INDEX_TO_SYMBOL.get(s_j, f"S{s_j}")
                write_sym  = self.INDEX_TO_SYMBOL.get(s_k, f"S{s_k}")
                next_state = f"q{q_m}"

                transition_table[(state, read_sym)] = (
                    write_sym, direction, next_state
                )

        return transition_table

    def _parse_instruction(self, inst: str) -> tuple:
        """
        Tek bir S.D talimatını ayrıştır.
        Format: DA...A DC...C DC...C L/R/N DA...A
        """
        tokens = []
        i = 0

        while i < len(inst):
            if inst[i] == 'D':
                i += 1
                count = 0
                char  = None
                while i < len(inst) and inst[i] in ('A', 'C'):
                    char = inst[i]
                    count += 1
                    i += 1
                tokens.append((char, count))

            elif inst[i] in ('L', 'R', 'N'):
                tokens.append(('dir', inst[i]))
                i += 1
            else:
                i += 1

        if len(tokens) < 5:
            return None

        q_i       = tokens[0][1]               # D + A*i → durum i
        s_j       = tokens[1][1]               # D + C*j → sembol j
        s_k       = tokens[2][1]               # D + C*k → yazılacak sembol k
        direction = tokens[3][1]               # L/R/N
        q_m       = tokens[4][1]               # D + A*m → sonraki durum m

        return (q_i, s_j, s_k, direction, q_m)


# ─────────────────────────────────────────────────────────────
# Universal Turing Machine
# Kaynak: Turing (1936), §6, s. 241-242
# ─────────────────────────────────────────────────────────────

class UniversalTuringMachine:
    """
    Evrensel Turing Makinesi.

    Turing §6 (s. 241):
    "It is possible to invent a single machine which can be used
    to compute any computable sequence. If this machine U is
    supplied with a tape on the beginning of which is written
    the S.D of some computing machine M, then U will compute
    the same sequence as M."

    Bu sınıf herhangi bir makinenin S.D veya D.N'sini alır
    ve o makinenin davranışını simüle eder.

    Kullanım:
        utm = UniversalTuringMachine()
        output = utm.run_from_sd(sd, max_steps=100)
        output = utm.run_from_dn(dn, max_steps=100)
    """

    def __init__(self):
        self.parser = SDParser()
        self.target_machine = None
        self.simulation_log = []

    def run_from_sd(
        self,
        sd: str,
        max_steps: int = 500,
        verbose: bool = False
    ) -> list:
        """
        S.D verilmiş bir makineyi simüle et.

        Args:
            sd:        Standard Description
            max_steps: Maksimum adım sayısı
            verbose:   Her adımı yazdır

        Returns:
            Hedef makinenin ürettiği 0/1 dizisi
        """
        transition_table = self.parser.parse(sd)

        if not transition_table:
            raise ValueError(f"Geçersiz S.D: {sd}")

        # Başlangıç durumu her zaman q1 (Turing §5, s. 239)
        self.target_machine = TuringMachine(
            transition_table=transition_table,
            initial_state='q1'
        )

        self.simulation_log = []

        for step in range(max_steps):
            state  = self.target_machine.state
            symbol = self.target_machine.read()
            key    = (state, symbol)

            log_entry = {
                'step':  step,
                'state': state,
                'head':  self.target_machine.head,
                'tape':  self.target_machine.get_tape_str(),
            }
            self.simulation_log.append(log_entry)

            if verbose and step < 20:
                print(
                    f"  Adım {step:3d} | "
                    f"Durum: {state:6s} | "
                    f"Okunan: {symbol!r:3s} | "
                    f"Bant: {self.target_machine.get_tape_str()}"
                )

            if key not in transition_table:
                if verbose:
                    print(f"  [Adım {step}] Makine durdu.")
                break

            self.target_machine.step()

        return self.target_machine.get_output()

    def run_from_dn(
        self,
        dn: str,
        max_steps: int = 500,
        verbose: bool = False
    ) -> list:
        """
        D.N verilmiş bir makineyi simüle et.
        D.N → S.D → simülasyon.

        Args:
            dn: Description Number

        Returns:
            Hedef makinenin ürettiği 0/1 dizisi
        """
        decoded = decode_description_number(dn)
        sd = decoded['sd']

        if verbose:
            print(f"D.N → S.D: {sd}")
            print()

        return self.run_from_sd(sd, max_steps=max_steps, verbose=verbose)

    def get_simulation_summary(self) -> dict:
        """Simülasyon özeti döndür."""
        if not self.simulation_log:
            return {}

        return {
            'total_steps': len(self.simulation_log),
            'states_visited': list({e['state'] for e in self.simulation_log}),
            'final_state': self.simulation_log[-1]['state'],
            'final_tape': self.target_machine.get_tape_str() if self.target_machine else '',
        }


# ─────────────────────────────────────────────────────────────
# Demo: U'nun §3 makinelerini simüle etmesi
# ─────────────────────────────────────────────────────────────

def demo_simulate_machine_1():
    """
    U, §3 Makine I'i (010101...) simüle ediyor.

    Makine I'in S.D'si (Turing s. 241):
        DADDCRDAA;DAADDRDAAA;DAAADDCCRDAAAA;DAAAADDRDA
    """
    print("Demo 1: U, §3 Makine I'i simüle ediyor (010101...)")
    print("Kaynak: Turing (1936), §6, s. 241-242")
    print("-" * 55)

    # §5'te doğruladığımız S.D
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
    dn = result['dn']

    print(f"Hedef makinenin S.D'si: {sd}")
    print(f"Hedef makinenin D.N'si: {dn}")
    print()
    print("U simülasyon adımları (ilk 20):")

    utm = UniversalTuringMachine()
    output = utm.run_from_sd(sd, max_steps=200, verbose=True)

    print()
    print(f"U'nun ürettiği dizi: {' '.join(output[:20])}")
    print(f"Beklenen            : 0 1 0 1 0 1 0 1 0 1 ...")

    summary = utm.get_simulation_summary()
    print()
    print(f"Toplam adım   : {summary['total_steps']}")
    print(f"Ziyaret edilen durumlar: {sorted(summary['states_visited'])}")
    print()


def demo_simulate_machine_2():
    """
    U, §3 Makine II'yi (001011011101111...) simüle ediyor.
    """
    print("Demo 2: U, §3 Makine II'yi simüle ediyor (001011...)")
    print("Kaynak: Turing (1936), §6, s. 241-242")
    print("-" * 55)

    states  = ['b', 'o', 'q', 'p', 'f']
    symbols = ['_', '0', '1', 'a', 'x']
    encoder = TuringMachineEncoder(states, symbols)

    transitions = [
        ('b', '_', 'a', 'R', 'b'),   # Basitleştirilmiş başlangıç
        ('o', '1', 'x', 'L', 'o'),
        ('o', '0', '0', 'R', 'q'),
        ('q', '0', '0', 'R', 'q'),
        ('q', '1', '1', 'R', 'q'),
        ('q', '_', '1', 'L', 'p'),
        ('p', 'x', '_', 'R', 'q'),
        ('p', 'a', 'a', 'R', 'f'),
        ('p', '0', '0', 'L', 'p'),
        ('p', '1', '1', 'L', 'p'),
        ('f', '0', '0', 'R', 'f'),
        ('f', '1', '1', 'R', 'f'),
        ('f', '_', '0', 'L', 'o'),
    ]

    result = encoder.encode_machine(transitions)
    sd = result['sd']

    print(f"Hedef makinenin S.D'si (kısaltılmış):")
    print(f"  {sd[:60]}...")
    print()

    utm = UniversalTuringMachine()
    output = utm.run_from_sd(sd, max_steps=1000, verbose=False)

    print(f"U'nun ürettiği dizi : {' '.join(output[:20])}")
    print(f"Beklenen            : 0 0 1 0 1 1 0 1 1 1 ...")
    print()


def demo_dn_input():
    """
    U'ya D.N ile girdi verme demosu.
    Turing §6: U, S.D'yi bantın başına yazılmış olarak alır.
    """
    print("Demo 3: U'ya D.N ile girdi verme")
    print("-" * 55)

    # §5'te hesapladığımız Makine I D.N'si
    dn = "31332531173113353111731113322531111731111335317"

    print(f"Girdi D.N: {dn}")
    print()

    utm = UniversalTuringMachine()
    output = utm.run_from_dn(dn, max_steps=200, verbose=False)

    print(f"Üretilen dizi: {' '.join(output[:20])}")
    print()


def show_universality_principle():
    """
    Evrensellik prensibini açıkla.
    Turing §6, s. 241-242.
    """
    print("Evrensellik Prensibi")
    print("Kaynak: Turing (1936), §6, s. 241-242")
    print("-" * 55)
    print()
    print("U → Evrensel Makine")
    print("M → Herhangi bir hesaplama makinesi")
    print()
    print("Çalışma prensibi:")
    print("  1. Bantın başına M'nin S.D'si yazılır")
    print("  2. U bu S.D'yi okur ve talimatları yorumlar")
    print("  3. U, M'nin ürettiği diziyi üretir")
    print()
    print("Modern bilgisayarla karşılaştırma:")
    print()
    print(f"  {'Turing (1936)':<25} {'Modern Bilgisayar'}")
    print(f"  {'-'*25} {'-'*25}")
    print(f"  {'S.D (Standard Desc.)':<25} Program / Kaynak Kod")
    print(f"  {'U (Evrensel Makine)':<25} CPU / İşlemci")
    print(f"  {'Bant':<25} RAM / Bellek")
    print(f"  {'m-konfigürasyon':<25} Register / İşlemci Durumu")
    print(f"  {'F-kareleri':<25} Çıktı Tamponu")
    print()
    print("Turing bunu 1936'da fiziksel bir bilgisayar olmadan,")
    print("yalnızca matematiksel ispat amacıyla geliştirdi.")
    print("Von Neumann 1945'te bu prensibi fiziksel makineye taşıdı.")


# ─────────────────────────────────────────────────────────────
# Çalıştır
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Turing (1936) §6 — Universal Computing Machine")
    print("=" * 60)
    print()

    show_universality_principle()
    print()

    demo_simulate_machine_1()
    demo_simulate_machine_2()
    demo_dn_input()

    print("─" * 60)
    print("Not: §8'de Turing bu U'yu kullanarak Halting Problem'in")
    print("çözümsüzlüğünü ispat edecek. Eğer bir makine D'nin")
    print("döngüsel olup olmadığını belirleyebilseydi, U ile")
    print("birleştirilerek bir çelişki üretilirdi.")
