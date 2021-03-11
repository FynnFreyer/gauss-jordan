from typing import List


class ErweiterteKoeffizientenMatrix:
    Vektor = List[float]
    Matrix = List[List[float]]

    def __init__(self, koeffizienten: Matrix, konstanten: Vektor):
        assert len(koeffizienten) >= 1 and len(konstanten), 'Leere Matrix übergeben'

        self.zeilen = len(koeffizienten)
        self.spalten = len(koeffizienten[0])

        assert all([len(zeile) == self.spalten for zeile in koeffizienten]), 'Zeilen haben ungleiche Länge'
        assert len(konstanten) == self.zeilen, 'Falsche Anzahl an Konstanten (Lösungen)'

        self._koeffs = koeffizienten
        self._konsts = konstanten

    def gib(self, zeile: int, spalte: int):
        """Gib Matrix[zeile][spalte] zurück (-1 steht für 'alle'/*)"""
        try:
            if zeile == -1 and spalte == -1:
                return [z[:] for z in self._koeffs][:]
            elif zeile == -1:
                return [z[spalte] for z in self._koeffs][:]
            elif spalte == -1:
                return self._koeffs[zeile][:]
            return self._koeffs[zeile][spalte]
        except IndexError:
            raise IndexError(f'Die Zeile {zeile}, oder die Spalte {spalte} existiert nicht')

    def tausche(self, zeile_a: int, zeile_b: int):
        """Tausche Zeile A mit Zeile B"""
        try:
            tmp = self._koeffs[zeile_b]
            self._koeffs[zeile_b] = self._koeffs[zeile_a]
            self._koeffs[zeile_a] = self._koeffs[zeile_b]

            tmp = self._konsts[zeile_b]
            self._konsts[zeile_b] = self._konsts[zeile_a]
            self._konsts[zeile_a] = self._konsts[zeile_b]
        except IndexError:
            raise IndexError(f'Die Zeile {zeile_a}, oder die Zeile {zeile_b} existiert nicht')

    def skaliere(self, zeile: int, skalar: float):
        """Multipliziere Zeile mit einem Skalar ungleich Null"""
        if skalar == 0:
            raise ValueError('Skalieren einer Zeile mit 0 ist verboten!')
        try:
            self._koeffs[zeile] = [koeff * skalar for koeff in self._koeffs[zeile]]
            self._konsts[zeile] = self._konsts[zeile] * skalar
        except IndexError:
            raise IndexError(f'Die Zeile {zeile} existiert nicht')

    def addiere(self, zeile_a: int, zeile_b: int, skalar=1):
        """Addiere Zeile A zu Zeile B und speichere das Ergebnis in Zeile B.
        Optional kann Zeile A vorher skaliert werden (die Skalierung wirkt sich nur auf die Zielzeile aus)"""
        assert zeile_a != zeile_b, 'Zeilen dürfen nicht zu sich selbst addiert werden, ' \
                                   'nutze alternativ die skaliere(zeile, skalar) Funktion'
        try:
            summanden_a = [koeff * skalar for koeff in self._koeffs[zeile_a]]
            summanden_b = [koeff for koeff in self._koeffs[zeile_b]]
            summen = [summand_a + summand_b for summand_a, summand_b in zip(summanden_a, summanden_b)]
            self._koeffs[zeile_b] = summen

            summand_a = self._konsts[zeile_a] * skalar
            summand_b = self._konsts[zeile_b]
            self._konsts[zeile_b] = summand_a + summand_b
        except IndexError:
            raise IndexError(f'Die Zeile {zeile_a}, oder die Zeile {zeile_b} existiert nicht')

    def gauss_jordan(self) -> Vektor:
        # für jede Zeile der Koeffizientenmatrix
        for momentane_zeile in range(self.zeilen):
            # finde die erste Spalte, welche unter der aktuellen Zeile einen Wert ungleich 0 hat
            # und merke dir Zeilenindex und Spaltenindex
            momentane_spalte = -1
            naechste_nicht_null_zeile = -1
            for spalte in range(momentane_zeile, self.spalten):
                spaltenvektor = self.gib(-1, spalte)
                if any([wert != 0 for wert in spaltenvektor[momentane_zeile:]]):
                    momentane_spalte = spalte
                    naechste_nicht_null_zeile = next(zeile for zeile, wert in enumerate(spaltenvektor)
                                                     if wert != 0 and zeile >= momentane_zeile)
                    break
            # wenn eine solche Zeile gefunden wurde
            if momentane_spalte != -1 and naechste_nicht_null_zeile != -1:
                spaltenvektor = self.gib(-1, momentane_spalte)

                # tausche sie mit der aktuellen Zeile
                if naechste_nicht_null_zeile != momentane_zeile:
                    self.tausche(momentane_zeile, naechste_nicht_null_zeile)

                # normiere die aktuelle Zeile, so dass der führende Wert 1 ist
                self.skaliere(momentane_zeile, 1/spaltenvektor[momentane_zeile])

                # lösche alle Nullen in der Spalte über- und unterhalb der aktuellen Zeile,
                # indem die aktuelle Zeile -M[zu_löschende_zeile][spalte] mal addiert wird
                for zeile, zeilen_wert in enumerate(spaltenvektor):
                    if zeile == momentane_zeile:
                        continue
                    if zeilen_wert != 0:
                        self.addiere(momentane_zeile, zeile, skalar=(-1)*zeilen_wert)

            print(self)

    def __str__(self):
        string_representation = ""

        laengster_eintrag = -1
        for zeilen_vektor in self._koeffs:
            for spalte in zeilen_vektor:
                laengster_eintrag = len(str(spalte)) if len(str(spalte)) > laengster_eintrag else laengster_eintrag
        padding = laengster_eintrag + 3

        start_zeile = "|--" + " "*((self.spalten*padding)-2) + "   |" + " "*padding + "--|"
        end_zeile = start_zeile

        string_representation += start_zeile + "\n"
        for zeile, zeilen_vektor in enumerate(self._koeffs):
            string = "|"
            for spalte in zeilen_vektor:
                string += '{0:{align}{padding}}'.format(spalte, align='>', padding=padding)
            string += "   |" + '{0:{align}{padding}}'.format(self._konsts[zeile], align='>', padding=padding) + "  |"
            string_representation += string + "\n"
        string_representation += end_zeile + "\n"

        return string_representation


if __name__ == '__main__':
    with open('koeffizienten') as f:
        koeffizienten = [[float(token.strip()) for token in line.split(',')] for line in f.readlines()]

    with open('konstanten') as f:
        konstanten = [float(line.strip()) for line in f.readlines()]

    matrix = ErweiterteKoeffizientenMatrix(koeffizienten, konstanten)
    print(matrix)
    matrix.gauss_jordan()
    print(matrix)


