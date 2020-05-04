////////// SCRIPT BEGIN //////////
// 緯度と経度の取得
var LAT = 35.69;
var LON = 139.75; 
function getLatLon() {
  if (navigator.geolocation) {
    var setLatLon = function (position) {
      LAT = position.coords.latitude;
      LON = position.coords.longitude;
    };
    navigator.geolocation.getCurrentPosition(setLatLon);
  };
}
// 地点リストの取得
var SDP_LIST = null;
function getSDP_LIST() {
  if (SDP_LIST != null) { return; };
  var req = new XMLHttpRequest();
  req.onreadystatechange = function() {
    if(req.readyState == 4 && req.status == 200){
      SDP_LIST = JSON.parse(req.responseText);
    }
  };
  req.open("GET", "./graph/sdp_list.json", false);
  req.send(null);
}
// 最寄り地点の検索
function getNearestSDP() {
  if (SDP_LIST == null) { return 44132; };
  const SDP = SDP_LIST["SDP"];
  const lat = SDP_LIST["lat"];
  const lon = SDP_LIST["lon"];
  var LL2 = [];
  for (let i in SDP) { LL2[i] = (LAT-lat[i])**2 + (LON-lon[i])**2; }
  var minLL2 = Math.min.apply(null,LL2);
  const i = LL2.indexOf(minLL2);
  return SDP[i];
};
function imaKoko(id) {
  // 時間
  const NOW = new Date();
  const TID = NOW.getFullYear() + ('0'+(NOW.getMonth()+1)).slice(-2) + ('0'+NOW.getDate()).slice(-2) + ('00'+Math.floor(NOW.getHours()/3)*3).slice(-2);
  // 場所
  getLatLon();
  getSDP_LIST();
  const SDP = getNearestSDP();
  url = "./graph/" + SDP + ".html#" + TID;
  //alert(url);
  document.getElementById(id).setAttribute('src', url);
  return false;
};
////////// SCRIPT END //////////

