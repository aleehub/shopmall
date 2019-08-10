var vm = new Vue({
    el: '.header_con',
    // 修改Vue变量的读取语法，避免和django模板语法冲突
    delimiters: ['[[', ']]'],
    data: {
        username: '',
    },
    mounted() {
        // 获取cookie中的用户名
        this.username = getCookie('username');
    }
});


// $(function () {
//     // 设置状态保持的用户名
//     set_username();
// });
//
// // 设置状态保持的用户名
// function set_username() {
// 	// 读取用户状态保持信息
// 	var username = getCookie('username');
// 	var $username;
// 	if (username) {
// 		$username =
// 			"欢迎您：<em>"+ username +"</em>\n" +
//             "\t\t\t\t\t<span>|</span>\n" +
//             "\t\t\t\t\t<a href='/logout/'>退出</a>";
//
// 		$('.login_btn').append($username);
// 	} else {
// 		$username = "<a href='/login/'>登录</a>\n" +
//             "\t\t\t\t\t<span>|</span>\n" +
//             "\t\t\t\t\t<a href='/register/'>注册</a>";
// 		$('.login_btn').append($username);
// 	}
// }