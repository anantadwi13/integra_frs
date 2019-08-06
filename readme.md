# Integra FRS
Bot auto frs integra

### Features
- Autologin
- Using multiple threads to send requests at a same time
- 2 methods to take class:
    - Sending requests by using auto fetch payload values
    - Force sending requests by using manual payloads
- Run at specific date & time

### Usage
```bash
python3 main.py
```

### Installation

1. Install dependencies
    ```bash
    pip3 install pycryptodome bs4 requests
    ``` 
2. Copy & edit config.json file
    ```bash
    cp config.json.example config.json
    ```
3. Run script
    ```bash
    python3 main.py
    ```
    
### Config
`username` - Username Integra  
`password` - Password Integra  
`nrp` - NRP Integra (Old NRP)  
`semester` - Current semester  
`tahun_ajaran` - Current academic year  
`pilihan_kelas` - Your selected classes  
`time_sleep` - Sleep time to start sending requests in next batch  
`mulai` - Start sending requests  
`time_ambil` - Date & time to start sending requests  
`format_value` - Format post fields  
`cookies_file` - Cookies file name  
`url_integra` - Integra URL  
`url_siakad` - SIAKAD URL  
