import undetected_chromedriver as uc

def get_driver(headless: bool = False):
    options = uc.ChromeOptions()
    if headless:
        options.add_argument('--headless=new')
    
    # uc maneja la mayoría de las opciones anti-detección automáticamente
    driver = uc.Chrome(version_main=143, options=options)
    return driver

def close_driver(driver):
    driver.quit()

#