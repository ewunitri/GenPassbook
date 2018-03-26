# GenPassbook
Generating bank passbook images

Release date: 26 March 2018


Update details:
- update .xml output to 20180326 version
  1.	<Page bbox=”x,y,w,h”>  to  <Page lefttop_x="0" lefttop_y="0" width=".." height="..">
  2.	<Passbookxxx bbox = “…”> to <Passbookxxx>
  3.	<TransactionRecordRow index = “x” > To <TransactionRecordRow> 
  4.	<Char bbox = “x,y,w,h”  value="承" font="AR_PL_UMing_TW_MBE_Light.ttf"/>
       To
      <Char lefttop_x="322" lefttop_y="251" width="35" height="34" value="承" font="AR_PL_UMing_TW_MBE_Light"/>
  5.	Font拿掉.ttf

- fix <AccoountField> typo -> <AccountField>
- fix a space does not need to be a <Char...>  



