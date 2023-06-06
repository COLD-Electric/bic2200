# bic2200 簡易安裝方式
windows環境下執行install.bat <br>
生成.whl檔於dist資料夾內 <br>
開啟cmd 輸入以下指令<br>
cd <whl檔所在位置> <br>
pip install <whl檔名.whl> <br>

<h1>#執行範例 </h1>
<br>
開啟cmd 輸入以下指令<br>
cd <下載資料夾所在位置>/example<br>
充電範例: python charge.py -v <設定電壓> -i <設定電流> Option <br>
Option: <br>
--max_charge 最大充電量設定(AH) <br>

放電範例: python discharge.py -v <設定電壓> -i <設定電流> Option <br>
Option: <br>
--max_discharge 最大放電量設定(AH) <br>

監控範例: python monitor.py <br>

