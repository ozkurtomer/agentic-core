## Ajan döngüsü

1. Ajanın kullanabileceği araçlar tanımlanır (isim, açıklama, parametreler).
2. Kullanıcının sorusu geçmişe eklenir.
3. Döngü başlar, en fazla N adım çalışır:
   a. Model tüm geçmişle çağrılır (model durumsuzdur, hafıza geçmişte).
   b. Modelin cevabı geçmişe eklenir.
   c. Model araç istemediyse: metin cevabı kullanıcıya gösterilir, döngü biter.
   d. Model araç istediyse: aracı MODEL DEĞİL, BENİM KODUM çalıştırır.
   e. Araç sonuçları geçmişe eklenir, döngü başa döner.
4. Limit dolarsa kullanıcı uyarılır.

## Güvenlik kuralları

- Sadece kayıtlı araçlar çalışır (beyaz liste).
- Araçlar sadece izin verilen verilere erişir; kilit kodda olur, açıklamada değil.
- Hatalar programı çökertmez, modele metin olarak döner.
