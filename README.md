### Trinn 1: Last ned Ubuntu Server
<ul>
   <li> Gå til Ubuntu-nettstedet (https://ubuntu.com/) og naviger til nedlastingssiden. </li>
   <li> Velg den nyeste versjonen av Ubuntu Server som er tilgjengelig for nedlasting. </li>
   <li> Klikk på nedlastingslenken for den valgte versjonen og last ned ISO-filen. </li>
</ul>

### Trinn 2: Opprett en ny virtuell maskin 

<ul>
    <li> Åpne din foretrukne virtualiseringsprogramvare (f.eks. VirtualBox eller VMware). </li>
    <li> Opprett en ny virtuell maskin ved å klikke på "Ny" eller "Opprett ny VM" -knappen. </li>
    <li> Gi den virtuelle maskinen et passende navn og velg "Linux" som operativsystem. </li>
    <li> Velg den anbefalte mengden minne (RAM) for Ubuntu Server (f.eks. 2 GB). </li>
    <li> Opprett en ny virtuell harddisk og tildel nok lagringsplass til VM-en (f.eks. 20 GB). </li>
    <li> Velg "Installer et operativsystem fra en ISO-fil" og velg deretter den tidligere nedlastede Ubuntu Server ISO-filen. </li>
</ul>

### Trinn 3: Installer Ubuntu Server 

<ul>
    <li> Start den virtuelle maskinen. </li>
    <li> Følg instruksjonene for å installere Ubuntu Server. Du kan godta standardinnstillingene for de fleste trinnene. </li>
    <li> Når du blir bedt om å velge programvare, velger du bare "OpenSSH Server". Flask vil bli installert senere. </li>
</ul>

### Trinn 4: Konfigurer nettverk 

<ul>
    <li> Etter at Ubuntu Server er installert, logg inn på den virtuelle maskinen med brukernavn og passord du opprettet under installasjonen. </li>
    <li> Skriv følgende kommando for å få IP-adressen til VM-en: </li>
</ul>
 
´´´sql
    ip addr show 
´´´
<ul>
   <li> Merk deg IP-adressen som er tildelt til den virtuelle maskinen. </li>
</ul>

### Trinn 5: Installer Flask og avhengigheter 

<ul>
    <li> Logg inn med brukernavnet og passordet for Ubuntu Server. </li>
    <li> Skriv følgende kommandoer for å installere Flask og dens avhengigheter: </li> 
</ul>

´´´sql
    sudo apt update 
    sudo apt install python3-pip 
    sudo pip3 install flask 
´´´
### Trinn 6: Lag en Flask-applikasjon 
<ul>
    <li> Opprett en ny fil med Python-kode for Flask-applikasjonen din. For eksempel kan du kalle den app.py og legge til følgende enkle Flask-kode: </li>
</ul>


```py from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, world!'

if __name__ == '__main__':
    app.run(host='0.0.0.0')`
```

### Trinn 7:

<ul> 
    <li> Kjør python fila, og eventuelt fiks de probleme du fikk hvis du fikk problemer </li>
    <li> Gå på nettleseren din å skriv inn IP-en du fikk fra trinn 4 </li>
    <li> Voilà! du har lagd din første Flask applikasjon </li>
</ul>