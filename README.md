# AlgoTrade 2024

## Zadatak - Trgovina energentima

_Note: Ovo je **first draft** zadatka, konačna verzija će biti detaljnija_

### Kratak opis

Igrači su podijeljeni u timove po 4 osobe te proizvode i trguju energentima na _simuliranom_ tržištu. Svaki tim na početku ima određena novčana sredstva s kojima mogu krenuti u proizvodnju energije tako što odabiru kakav će tip elektrane raditi. Potom proizvode i prodaju energiju te iz zarade grade nove elektrane itd. Sve je simulirano unutar vremena od 20-ak godina, a boduje se zarada ostvarena na kraju tog perioda (ideja je slična igri [Factorio](https://www.factorio.com/)).

Igračima se na raspolaganje daju različiti načini proizvodnje, od onih **tromih** do **fleksibilnijih**. Tromi načini su plinske elektrane i elektrane na ugljen koje su vrlo efikasne, no paljenje i mirovanje je skupo te trebaju vrijeme i dodatne resurse pri prvom pokretanju. Manje trome su hidroelektrane dok vjetroelektrane i solarne elektrane ne trebaju resurse, ali skupe su za postavljanje i imaju nepredvidiv rezultat zbog vanjskih uvjeta. Nuklearna energija je konačan cilj, ali moguća će biti tek pred kraj igre zbog dugog vremena izgradnje i velike cijene.

### Datascience aspekt

Potrošači energije su modelirani tako da prate distribuciju i sezonalnost stvarne potrošnje koja varira o dobu dana, godišnjem dobu i temperaturi. U simulaciji bi za njih preuzeli stvarne podatke kako bi igrači mogli koristiti i datascience pristup pri osmišljavanju strategije.

Podatci o potrošnji i cijeni energenata se mijenjaju svake sekunde, a to vrijeme nazivamo **tick**.

### Mogućnosti igre

Zbog prirode trgovine električnom energijom i njene nemogućnosti skladištenja, igračima je cilj u svakom trenu proizvoditi onoliko energije koliko mogu prodati. Ako proizvedu previše energije, na kraju tick-a igre im se **oduzima** cijena viška energije pomnožena koeficijentom penalizacije.

Energenti kojima se trguje su struja, nafta, plin, biomasa, uranij i sl. Na početku ih je jedino moguće kupiti, a kasnije se mogu proizvoditi u rudnicima. U srednjem i konačnom stadiju igre, bit će moguće **_skladištiti energiju_** npr. bržim elektranama, pretvaranjem nafte i plina u energiju ili otključavanjem baterija u vjetroelektranama.

Svaki tim igra za sebe, ali njihove akcije utječu na ukupno stanje tržišta. Ukoliko je npr. puno električne energije dostupno, njena cijena pada i sl. Timovi neće činiti tržište sami za sebe nego će biti mali dio jednog većeg tržišta koje će se regulirati stvarnim podatcima. 
