# MPD Dsiplay on I2C-OLED

秋月電子のSO1602AW というI2C-OLEDを使ってMPDの曲名を表示するpythonスクリプトです。

![http://nw-electric.way-nifty.com/photos/uncategorized/2016/09/14/oled_r3.jpg](http://nw-electric.way-nifty.com/photos/uncategorized/2016/09/14/oled_r3.jpg)



### 導入方法

volumio2への導入方法です。

```
sudo apt-get update
```

少々待ちます。　

```
sudo apt-get install python-smbus kakasi

git clone https://github.com/Takazine/mpd_oled_ctrl.git

cd mpd_oled_ctrl

sudo chmod +x oled_ctrl_s.py

sudo cp oled_ctrl.service /etc/systemd/system/oled_ctrl.service
```

途中でパスワードを求められたら **volumio** と答えます。

 [oled_ctrl.service](oled_ctrl.service) 

つづいて、systemdに登録します。

```
sudo systemctl enable oled_ctrl
```



最後にI2C通信をイネーブルしておきます。

**/etc/modules**   に  **i2c-dev** が記載されていること

**/boot/config.txt**   に **dtparam=i2c_arm=on**  が記載されていること

記載がなければテキストエディタで追記します。

ここでvolumio2を再起動すると、OLEDに曲名が表示されます。



------

### 応用編

RaspbianやMoode Audioへ登録するときはoled_ctrl.serviceの

/home/**volumio**/mpd_oled_ctrl/oled_ctrl_s.py    を
/home/**pi**/mpd_oled_ctrl/oled_ctrl_s.py         に変更します。　　

