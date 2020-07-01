## Metaheurystics - Post Correspondence Problem
### Michał Zaremba

(Python)Projekt robiony w ramach przedmiotu na studia noszącego nazwę Metaheurystyki. Moim zadaniem było rozwiązać zadany problem używając metaheurystyk, takich jak: Brute Force, Hill Climbing, czy Tabu.<br>
Post Correspondence Problem - Przykład nierozstrzygalnego problemu decyzyjnego.<br>
  Z przykładowych list z wartościami stringowymi:<br>
  a1:a, a2:ab, a3:bba<br>
  b1:baa, b2:aa, b3:bb<br>
  Znaleźć rozwiązaniie które dla obu list będzie wyglądało tak samo. Rozwiązaniem powyższego przykładu będzie kolejność (3,2,3,1), ponieważ:<br>
  a3a2a3a1  = bba ab bba a <br>
  b3b2b3b1 = bb aa bb baa <br>
  <br>
test.json - trudny problem do rozwiązania, działa na nim tylko Bruteforce - był to test czy program, na pewno znajdzie prawidłowe rozwiązanie.<br>
testEasy.json - łatwy problem do rozwiązania, wszystkie metody działają. Z racji, że inicjacja jest przypadkowa tabu może znajdować zły wynik.<br>
