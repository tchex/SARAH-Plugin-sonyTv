exports.action = function(data, callback, config, SARAH){
config = config.modules.sonyTv;
if (!config.ip){
		console.log("La variable url n'est pas configurée");
		return callback({'tts' : "La variable adresse n'est pas configurée"})};
if (!config.mac){
		console.log("La variable MAC n'est pas configurée");
		return callback({'tts' : "La variable adresse MAC n'est pas configurée"})};		
if (!config.key){
		key=':0000'
}
else{
	key=":" + config.key;
	}

execprocess(data.sonyTv);
callback({ 'tts': data.callback});

	
function execprocess(command){
	var exec = require('child_process').exec;
	var process = __dirname+'\\lib\\sony.py '+command+' '+config.ip+' '+key+' '+config.mac;
	var child = exec(process,
	function (error, stdout, stderr) {
	})};
};