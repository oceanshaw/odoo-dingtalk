
DingTalkPC.config({
    agentId: _config.agentId,
    corpId: _config.corpId,
    timeStamp: _config.timeStamp,
    nonceStr: _config.nonceStr,
    signature: _config.signature,
    jsApiList: [
        'runtime.permission.requestAuthCode',
        'device.notification.alert',
        'device.notification.confirm',
        'biz.contact.choose',
        'device.notification.prompt',
        'biz.ding.post'
    ]
});


DingTalkPC.userid=0;
DingTalkPC.ready(function(res){
    console.log('test ready')
    crsf = document.getElementById("csrf_token").value
    DingTalkPC.runtime.permission.requestAuthCode({
        corpId: _config.corpId, //企业ID
        onSuccess: function(info) {
            console.log(info)
            console.log(crsf)
	        $.ajax({
                url: '/dingtalk/getuserinfo',
                type:"GET",
                data: {"crsf":crsf, "code":info.code},
                dataType:'json',
                timeout: 900,
                success: function (data) {
                    console.log(data)
//                    var result = JSON.parse(data);
                    window.location.href = '/'
//                    if (result.status === 0) {
//                        DingTalkPC.userid = result.data.userid;
//                    } else {
//                        DingtalkMessageAlert('自动授权失败，前往登录')
//                    }
//                        DingTalkPC.biz.util.openLink({
//                          url:"http://www.baidu.com",
//                          onSuccess : function(result) {
//                               alert("1234");
//                          },
//                          onFail : function(err) {
//                               console.log(err)
//                          }
//                      });
                },
                error: function (data) {
                    DingtalkMessageAlert('自动授权失败，前往登录')
                }
            });
        },
        onFail : function(err) {
            DingtalkMessageAlert('自动授权失败，前往登录')
        }
    });
});

function DingtalkMessageAlert(msg) {
    DingTalkPC.device.notification.alert({
    message: msg,
    title: "",//可传空
    buttonName: "确认",
    onSuccess: function () {
        //onSuccess将在点击button之后回调
        /*回调*/
        window.location.href = '/'
    },
    onFail: function (err) { }
});
}

DingTalkPC.error(function(error){
    console.log(error)
  /*{
      errorCode: 1001, //错误码
      errorMessage: '', //错误信息
  }*/
  // config信息验证失败会执行error函数，如签名过期导致验证失败，具体错误信息可以打开调试窗口的 console查看，也可以在返回的res参数中查看。
});