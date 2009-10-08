<html>
  <head>
    <title>webshot</title>
  </head>
  <body>
    <h1>webshot</h1>
    
    <p>ウェブページを画像へ変換できます。</p>
    
    <form method="GET" action="webshot.cgi">
      <p>URL: <input type="text" name="url">
	<select name="s">
	  <option value="1">640x480
	  <option value="2">800x600
	  <option value="3">1024x768
	  <option value="0">full
      </select></p>
      <input type="submit" value="shot!">
      <input type="reset" value="reset">
    </form>
    <br>
    <h2>Last images...</h2>
    <p>
      <?php
	 // Config
	 $file = "./cnt_log";
	 $lastn = "12";
	 //
	 
	 if(file_exists($file)) {
	   $cnt = file_get_contents($file);
	 }
	 else {
	   $cnt = 0;
	 }
	 
	 if($cnt) {
           $cnt = (int)$cnt;
	 }
	 else {
	   $cnt = 0;
	   echo "<p>No image...</p>";
	 }
	 
	 for($i = $cnt - 1, $j = 1; $i >= $cnt - (int)$lastn && $i > 0; $i--, $j++) {
           $num = sprintf("%03d", $i);
      
           $img = "img/webshot_" . $num . ".png";
           $imgt = "img/webshot-thumb_" . $num . ".png";
      
           echo '<a href="' . $img . '"><img src="' . $imgt . '" border="0"></a>';
           if(!($j % 4)) { echo "<br>\n"; }
         }
      ?>
    </p>
    
    <h3>Changes</h3>
    <p>Changes in v1.30 (09/10/09)</p>
    <ul>
      <li>split config file</li>
    </ul>
    <p>Changes in v1.27 (09/10/08)</p>
    <ul>
      <li>bug fix</li>
    </ul>
    <p>Changes in v1.26 (09/02/22)</p>
    <ul>
      <li>Iceweasel Support</li>
      <li>https Support</li>
      <li>security fix</li>
      <li>bug fix</li>
    </ul>
    <p>Changes in v1.25 (08/12/30)</p>
    <ul>
      <li>url GET support</li>
      <li>show processing time</li>
      <li>bug fix</li>
    </ul>
    
    <p>webshot-v1.30</p>
    <hr>
    <p><a href="http://hogehoge/">hogehogehoge</a></p>
  </body>
</html>
