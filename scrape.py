from playwright.sync_api import sync_playwright
from dataclasses import dataclass, asdict, field
import pandas as pd
import mysql.connector
import argparse
import os
import sys

def scrape():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="secret",
        database="cafelogy",
        auth_plugin="mysql_native_password"
    )
    if db.is_connected():
        cursor = db.cursor()

        cursor.execute("SELECT * FROM cafes WHERE temp_image IS NULL AND image = 'pending'")
        data = cursor.fetchall()

        for x in data:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)    
                page = browser.new_page()
                    
                url = "https://www.google.com/maps/place/?q=place_id:" + x[5]
                
                page.goto(url)

                page.wait_for_timeout(2000)
                try:
                    img = page.locator('//button[@jsaction="pane.wfvdle11.heroHeaderImage"]//img[@decoding="async"]').get_attribute('src')
                    cursor.execute(f"UPDATE `cafes` SET `temp_image`='{img}', `image`='success' WHERE `places_id` = '{x[5]}'")
                    db.commit()
                except:
                    cursor.execute(f"UPDATE `cafes` SET `image`='failed' WHERE `places_id` = '{x[5]}'")
                    db.commit()
                    print('Error')
                
                browser.close()
        


if __name__ == "__main__":
    scrape()