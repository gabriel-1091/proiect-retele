


Executia paralela la
     distanta:



○      Clientii incearca sa se
conecteze pe rand la o lista de server-e, oprindu-se dupa ce reusesc sa se
conecteze la primul;



○      Clientul este la randul sau
server, iar cand se conectaza la un server, ii trimite portul pe care asculta
la randul sau sa primeasca procesari;



○      Acesti clienti notifica la
randul lor clientii lor cu privire la intrare unui nou client in cluster;



○      Server-ul la care se
conecteaza un client notifica restul clientilor conectati cu privire la adresa
si portul unde poate fi contactat clientul acceptat;



○      Un client poate solicita
serverului cu cel mai mic grad de incarcare sa execute pe un numar de fire de
executie in paralele o metoda a unei clase care intoarce un anumit rezultat;



○      In cazul in care clasa
respectiva nu se gaseste pe server-ul destinatie, clientul trimite continutul
binar al clasei server-ului;



○      Server-ul lanseaza in exeutie
metoda pe numarul de fire de executie solicitat de client si cu argumentele
primite de la acesta;



○      Server-ul notifica toti
clientii conectati la el pentru actualizarea gradului de incarcare cu
procesarile primite sa le execute, precum si server-ul la care e el conectat,
care atunci cand primeste notificarea in cauza, notifica la randul sau toti
clientii care sunt conectati la el in acest sens;



○      Cand server-ul a obtinut
rezultatul in urma executiei unui fir, il trimite clientului si notifica toti
clientii conectati la el pentru actualizarea gradului sau de incarcare, acestia
notificand la randul lor clientii conectati la ei;



○      Cand un client se
deconecteaza, server-ul la care e conectat notifica toti clientii conectati la
el, care la randul lor isi notifica si ei clientii conectati la ei.


