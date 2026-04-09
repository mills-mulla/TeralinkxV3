const __vite__mapDeps=(i,m=__vite__mapDeps,d=(m.f||(m.f=["assets/Auth-DRKe7qZ-.js","assets/vue-vendor-C3IK7onx.js","assets/charts-CY_xae0W.js","assets/Dashboard-GPgSYzCF.js","assets/utils-DDk3lJ3U.js","assets/rolldown-runtime-DGruFWvd.js","assets/Clients-D0WDNodq.js","assets/Users-DxFJBfet.js","assets/Devices-CdBilu0F.js","assets/Sessions-ieNgBXfP.js","assets/Packages-CPV9tkk6.js","assets/Vouchers-t6ZdL_at.js","assets/Coupons-McJaEr4y.js","assets/Promotions-BMvV-8SB.js","assets/PointTransactions-CvXFc106.js","assets/Locations-CRz5OZic.js","assets/Transactions-Dj-DLjwB.js","assets/Refunds-DdutsYds.js"])))=>i.map(i=>d[i]);
import { r as __toESM } from "./rolldown-runtime-DGruFWvd.js";
import { $ as reactive, A as vModelText, B as createTextVNode, C as createPinia, D as vModelCheckbox, E as createApp, F as createBaseVNode, G as openBlock, H as h, I as createBlock, J as resolveComponent, K as renderList, L as createCommentVNode, M as withModifiers, N as Fragment, O as vModelDynamic, P as computed, Q as withDirectives, R as createElementBlock, S as m, T as TransitionGroup, U as onMounted, V as createVNode, W as onUnmounted, X as watch, Y as resolveDynamicComponent, Z as withCtx, _ as render$13, a as render$11, b as render$9, c as render$18, d as render$2, et as ref, f as render$3, g as render$14, h as render$6, i as render$1, j as vShow, k as vModelSelect, l as render$10, m as render$7, n as createWebHistory, nt as normalizeStyle, o as render$16, p as render$4, q as renderSlot, r as render$8, rt as toDisplayString, s as render, t as createRouter, tt as normalizeClass, u as render$17, v as render$12, w as Transition, x as render$15, y as render$5, z as createStaticVNode } from "./vue-vendor-C3IK7onx.js";
import { n as require_pusher, t as axios_default } from "./utils-DDk3lJ3U.js";
import "./charts-CY_xae0W.js";
(function polyfill() {
	const relList = document.createElement("link").relList;
	if (relList && relList.supports && relList.supports("modulepreload")) return;
	for (const link of document.querySelectorAll("link[rel=\"modulepreload\"]")) processPreload(link);
	new MutationObserver((mutations) => {
		for (const mutation of mutations) {
			if (mutation.type !== "childList") continue;
			for (const node of mutation.addedNodes) if (node.tagName === "LINK" && node.rel === "modulepreload") processPreload(node);
		}
	}).observe(document, {
		childList: true,
		subtree: true
	});
	function getFetchOpts(link) {
		const fetchOpts = {};
		if (link.integrity) fetchOpts.integrity = link.integrity;
		if (link.referrerPolicy) fetchOpts.referrerPolicy = link.referrerPolicy;
		if (link.crossOrigin === "use-credentials") fetchOpts.credentials = "include";
		else if (link.crossOrigin === "anonymous") fetchOpts.credentials = "omit";
		else fetchOpts.credentials = "same-origin";
		return fetchOpts;
	}
	function processPreload(link) {
		if (link.ep) return;
		link.ep = true;
		const fetchOpts = getFetchOpts(link);
		fetch(link.href, fetchOpts);
	}
})();
var isDark = ref(false);
var isAuto = ref(false);
function useTheme() {
	const setTheme = (dark) => {
		console.log("🎨 Setting theme to:", dark ? "dark" : "light");
		isDark.value = dark;
		const html = document.documentElement;
		if (dark) {
			html.classList.add("dark");
			console.log("✅ Added dark class to html");
		} else {
			html.classList.remove("dark");
			console.log("✅ Removed dark class from html");
		}
		localStorage.setItem("theme", dark ? "dark" : "light");
		console.log("💾 Saved theme to localStorage:", dark ? "dark" : "light");
	};
	const toggleTheme = () => {
		console.log("🔄 Toggle theme clicked");
		isAuto.value = false;
		localStorage.setItem("themeAuto", "false");
		setTheme(!isDark.value);
	};
	const setAutoTheme = (auto) => {
		console.log("⚙️ Set auto theme:", auto);
		isAuto.value = auto;
		localStorage.setItem("themeAuto", auto ? "true" : "false");
		if (auto) applyAutoTheme();
	};
	const applyAutoTheme = () => {
		const hour = (/* @__PURE__ */ new Date()).getHours();
		const shouldBeDark = hour >= 18 || hour < 6;
		console.log("🕐 Auto theme - Hour:", hour, "Should be dark:", shouldBeDark);
		setTheme(shouldBeDark);
	};
	const initTheme = () => {
		console.log("🚀 Initializing theme...");
		const savedAuto = localStorage.getItem("themeAuto");
		const savedTheme = localStorage.getItem("theme");
		console.log("📦 Saved auto:", savedAuto, "Saved theme:", savedTheme);
		if (savedAuto === "true") {
			isAuto.value = true;
			applyAutoTheme();
			setInterval(applyAutoTheme, 6e4);
		} else if (savedTheme) {
			isAuto.value = false;
			setTheme(savedTheme === "dark");
		} else {
			isAuto.value = false;
			setTheme(false);
		}
	};
	return {
		isDark,
		isAuto,
		toggleTheme,
		setAutoTheme,
		initTheme
	};
}
var __plugin_vue_export_helper_default = (sfc, props) => {
	const target = sfc.__vccOpts || sfc;
	for (const [key, val] of props) target[key] = val;
	return target;
};
var _sfc_main$43 = {
	name: "Sidebar",
	props: {
		stats: {
			type: Object,
			default: () => ({
				activeUsers: 0,
				activeSessions: 0,
				activeDevices: 0,
				pendingRefunds: 0
			})
		},
		isMobileOpen: {
			type: Boolean,
			default: false
		}
	},
	emits: [
		"component-selected",
		"refresh-data",
		"close-mobile",
		"sidebar-toggle"
	],
	setup() {
		const { isDark: isDark$1, isAuto: isAuto$1, toggleTheme, setAutoTheme } = useTheme();
		const handleAutoThemeChange = () => {
			setAutoTheme(isAuto$1.value);
		};
		return {
			isDark: isDark$1,
			isAuto: isAuto$1,
			toggleTheme,
			setAutoTheme,
			handleAutoThemeChange
		};
	},
	data() {
		return {
			activeComponent: "Dashboard",
			isMobile: false,
			isCollapsed: false,
			overviewItems: [{
				id: 1,
				name: "Dashboard",
				icon: "<svg class=\"w-5 h-5\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z\"/></svg>",
				component: "Dashboard",
				color: "#3b82f6"
			}, {
				id: 2,
				name: "Analytics",
				icon: "<svg class=\"w-5 h-5\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z\"/></svg>",
				component: "Analytics",
				color: "#8b5cf6"
			}],
			userManagementItems: [
				{
					id: 3,
					name: "Clients",
					icon: "<svg class=\"w-5 h-5\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z\"/></svg>",
					component: "Clients",
					color: "#10b981"
				},
				{
					id: 4,
					name: "Users",
					icon: "<svg class=\"w-5 h-5\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z\"/></svg>",
					component: "Users",
					color: "#a855f7"
				},
				{
					id: 5,
					name: "Devices",
					icon: "<svg class=\"w-5 h-5\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M17 1.01L7 1c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-1.99-2-1.99zM17 19H7V5h10v14z\"/></svg>",
					component: "Devices",
					color: "#06b6d4"
				},
				{
					id: 6,
					name: "Sessions",
					icon: "<svg class=\"w-5 h-5\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z\"/></svg>",
					component: "Sessions",
					color: "#f97316"
				}
			],
			productsItems: [
				{
					id: 7,
					name: "Packages",
					icon: "<svg class=\"w-5 h-5\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4zM6 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm13.5-9l1.96 2.5H17V9.5h2.5zm-1.5 9c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z\"/></svg>",
					component: "Packages",
					color: "#6366f1"
				},
				{
					id: 8,
					name: "Vouchers",
					icon: "<svg class=\"w-5 h-5\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7C4.67 7 4 6.33 4 5.5S4.67 4 5.5 4 7 4.67 7 5.5 6.33 7 5.5 7z\"/></svg>",
					component: "Vouchers",
					color: "#ec4899"
				},
				{
					id: 9,
					name: "Coupons",
					icon: "<svg class=\"w-5 h-5\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M20 4H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z\"/></svg>",
					component: "Coupons",
					color: "#f43f5e"
				},
				{
					id: 10,
					name: "Promotions",
					icon: "<svg class=\"w-5 h-5\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-5.5-2.5l7.51-3.49L17.5 6.5 9.99 9.99 6.5 17.5zm5.5-6.6c.61 0 1.1.49 1.1 1.1s-.49 1.1-1.1 1.1-1.1-.49-1.1-1.1.49-1.1 1.1-1.1z\"/></svg>",
					component: "Promotions",
					color: "#f59e0b"
				}
			],
			financialItems: [
				{
					id: 11,
					name: "Finance",
					icon: "<svg class=\"w-5 h-5\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z\"/></svg>",
					component: "Finance",
					color: "#8b5cf6"
				},
				{
					id: 12,
					name: "Transactions",
					icon: "<svg class=\"w-5 h-5\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M20 4H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z\"/></svg>",
					component: "Transactions",
					color: "#14b8a6"
				},
				{
					id: 13,
					name: "Refunds",
					icon: "<svg class=\"w-5 h-5\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z\"/></svg>",
					component: "Refunds",
					color: "#ef4444"
				}
			],
			networkItems: [{
				id: 14,
				name: "Locations",
				icon: "<svg class=\"w-5 h-5\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z\"/></svg>",
				component: "Locations",
				color: "#22c55e"
			}],
			supportMenuItems: [
				{
					id: 15,
					name: "Documentation",
					icon: "<svg class=\"w-5 h-5\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z\"/></svg>",
					component: "Auth"
				},
				{
					id: 16,
					name: "Help Center",
					icon: "<svg class=\"w-5 h-5\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z\"/></svg>",
					component: "Gallery"
				},
				{
					id: 17,
					name: "System Info",
					icon: "<svg class=\"w-5 h-5\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M13 2.05v3.03c3.39.49 6 3.39 6 6.92 0 .9-.18 1.75-.48 2.54l2.6 1.53c.56-1.24.88-2.62.88-4.07 0-5.18-3.95-9.45-9-9.95zM12 19c-3.87 0-7-3.13-7-7 0-3.53 2.61-6.43 6-6.92V2.05c-5.06.5-9 4.76-9 9.95 0 5.52 4.47 10 9.99 10 3.31 0 6.24-1.61 8.06-4.09l-2.6-1.53C16.17 17.98 14.21 19 12 19z\"/></svg>",
					component: "Vision"
				},
				{
					id: 18,
					name: "About",
					icon: "<svg class=\"w-5 h-5\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z\"/></svg>",
					component: "About"
				}
			]
		};
	},
	methods: {
		selectComponent(componentName) {
			this.activeComponent = componentName;
			this.$emit("component-selected", componentName);
			if (this.isMobile) this.$emit("close-mobile");
		},
		toggleSidebar() {
			this.isCollapsed = !this.isCollapsed;
			this.$emit("sidebar-toggle", this.isCollapsed);
		},
		getBadgeCount(component) {
			return {
				"Users": this.stats.activeUsers,
				"Sessions": this.stats.activeSessions,
				"Devices": this.stats.activeDevices,
				"Refunds": this.stats.pendingRefunds
			}[component] || 0;
		},
		checkMobile() {
			this.isMobile = window.innerWidth < 1024;
		}
	},
	mounted() {
		this.$emit("component-selected", this.activeComponent);
		this.checkMobile();
		window.addEventListener("resize", this.checkMobile);
	},
	beforeUnmount() {
		window.removeEventListener("resize", this.checkMobile);
	}
};
var _hoisted_1$43 = { class: "p-5 border-b border-slate-200 dark:border-slate-700 bg-gradient-to-r from-blue-500/10 to-purple-600/10" };
var _hoisted_2$43 = {
	key: 0,
	class: "flex items-center space-x-3"
};
var _hoisted_3$43 = {
	key: 1,
	class: "flex justify-center"
};
var _hoisted_4$43 = {
	key: 0,
	class: "p-4 border-b border-slate-200 dark:border-slate-800"
};
var _hoisted_5$43 = { class: "grid grid-cols-2 gap-2" };
var _hoisted_6$43 = { class: "bg-blue-50 dark:bg-blue-500/10 rounded-lg p-2" };
var _hoisted_7$42 = { class: "text-lg font-bold text-blue-700 dark:text-blue-300" };
var _hoisted_8$40 = { class: "bg-emerald-50 dark:bg-emerald-500/10 rounded-lg p-2" };
var _hoisted_9$38 = { class: "text-lg font-bold text-emerald-700 dark:text-emerald-300" };
var _hoisted_10$36 = { class: "bg-purple-50 dark:bg-purple-500/10 rounded-lg p-2" };
var _hoisted_11$31 = { class: "text-lg font-bold text-purple-700 dark:text-purple-300" };
var _hoisted_12$31 = { class: "bg-amber-50 dark:bg-amber-500/10 rounded-lg p-2" };
var _hoisted_13$31 = { class: "text-lg font-bold text-amber-700 dark:text-amber-300" };
var _hoisted_14$31 = { class: "flex-1 py-6 overflow-y-auto" };
var _hoisted_15$31 = { class: "px-4 space-y-1" };
var _hoisted_16$31 = {
	key: 0,
	class: "px-3 py-2"
};
var _hoisted_17$31 = ["onClick", "title"];
var _hoisted_18$31 = ["innerHTML"];
var _hoisted_19$27 = {
	key: 0,
	class: "flex-1"
};
var _hoisted_20$27 = {
	key: 1,
	class: "px-3 py-2 mt-4"
};
var _hoisted_21$26 = {
	key: 2,
	class: "border-t border-slate-200 dark:border-slate-700 my-2"
};
var _hoisted_22$26 = ["onClick", "title"];
var _hoisted_23$25 = ["innerHTML"];
var _hoisted_24$24 = {
	key: 0,
	class: "flex-1"
};
var _hoisted_25$24 = {
	key: 3,
	class: "px-3 py-2 mt-4"
};
var _hoisted_26$24 = {
	key: 4,
	class: "border-t border-slate-200 dark:border-slate-700 my-2"
};
var _hoisted_27$23 = ["onClick", "title"];
var _hoisted_28$23 = ["innerHTML"];
var _hoisted_29$23 = {
	key: 0,
	class: "flex-1"
};
var _hoisted_30$22 = {
	key: 5,
	class: "px-3 py-2 mt-4"
};
var _hoisted_31$21 = {
	key: 6,
	class: "border-t border-slate-200 dark:border-slate-700 my-2"
};
var _hoisted_32$20 = ["onClick", "title"];
var _hoisted_33$20 = ["innerHTML"];
var _hoisted_34$20 = {
	key: 0,
	class: "flex-1"
};
var _hoisted_35$19 = {
	key: 7,
	class: "px-3 py-2 mt-4"
};
var _hoisted_36$19 = {
	key: 8,
	class: "border-t border-slate-200 dark:border-slate-700 my-2"
};
var _hoisted_37$19 = ["onClick", "title"];
var _hoisted_38$19 = ["innerHTML"];
var _hoisted_39$19 = {
	key: 0,
	class: "flex-1"
};
var _hoisted_40$19 = {
	key: 9,
	class: "px-3 py-2 mt-4"
};
var _hoisted_41$18 = {
	key: 10,
	class: "border-t border-slate-200 dark:border-slate-700 my-2"
};
var _hoisted_42$16 = ["onClick", "title"];
var _hoisted_43$15 = ["innerHTML"];
var _hoisted_44$15 = { key: 0 };
var _hoisted_45$12 = { class: "border-t border-slate-200 dark:border-slate-800" };
var _hoisted_46$12 = {
	class: "w-4 h-4",
	fill: "none",
	stroke: "currentColor",
	viewBox: "0 0 24 24"
};
var _hoisted_47$11 = ["d"];
var _hoisted_48$8 = { class: "p-4 space-y-3" };
var _hoisted_49$8 = {
	key: 0,
	class: "bg-gradient-to-r from-slate-100 to-slate-200 dark:from-slate-800 dark:to-slate-700 rounded-xl p-3 shadow-sm"
};
var _hoisted_50$8 = { class: "flex items-center justify-between mb-2" };
var _hoisted_51$8 = {
	key: 0,
	class: "w-4 h-4",
	fill: "none",
	viewBox: "0 0 24 24",
	stroke: "currentColor"
};
var _hoisted_52$7 = {
	key: 1,
	class: "w-4 h-4",
	fill: "currentColor",
	viewBox: "0 0 20 20"
};
var _hoisted_53$7 = { class: "flex items-center cursor-pointer" };
var _hoisted_54$6 = {
	key: 1,
	class: "flex justify-center"
};
var _hoisted_55$5 = {
	key: 0,
	class: "w-4 h-4",
	fill: "none",
	viewBox: "0 0 24 24",
	stroke: "currentColor"
};
var _hoisted_56$4 = {
	key: 1,
	class: "w-4 h-4",
	fill: "currentColor",
	viewBox: "0 0 20 20"
};
var _hoisted_57$4 = {
	key: 2,
	class: "flex items-center justify-between text-xs"
};
var _hoisted_58$4 = {
	key: 3,
	class: "flex justify-center"
};
function _sfc_render$43(_ctx, _cache, $props, $setup, $data, $options) {
	return openBlock(), createElementBlock("div", null, [$props.isMobileOpen && $data.isMobile ? (openBlock(), createElementBlock("div", {
		key: 0,
		class: "fixed inset-0 bg-black/60 backdrop-blur-sm lg:hidden",
		style: { "z-index": "45" },
		onClick: _cache[0] || (_cache[0] = ($event) => _ctx.$emit("close-mobile"))
	})) : createCommentVNode("", true), createBaseVNode("aside", {
		class: normalizeClass(["bg-white dark:bg-slate-900 shadow-xl flex flex-col h-screen fixed left-0 top-0 border-r border-slate-200 dark:border-slate-800 transition-all duration-300", {
			"-translate-x-full lg:translate-x-0": !$props.isMobileOpen,
			"translate-x-0": $props.isMobileOpen,
			"w-56": !$data.isCollapsed,
			"w-16": $data.isCollapsed
		}]),
		style: { "z-index": "50" }
	}, [
		createBaseVNode("div", _hoisted_1$43, [!$data.isCollapsed ? (openBlock(), createElementBlock("div", _hoisted_2$43, [..._cache[6] || (_cache[6] = [createBaseVNode("img", {
			src: "/su/assets/teralinkx2-D-ymN_3H.png",
			alt: "Teralinkx Logo",
			class: "h-10 w-auto object-contain"
		}, null, -1), createBaseVNode("div", null, [createBaseVNode("h1", { class: "text-base font-bold text-slate-900 dark:text-white" }, "TERALINKX"), createBaseVNode("p", { class: "text-slate-500 dark:text-slate-400 text-xs font-medium" }, "Admin Panel")], -1)])])) : (openBlock(), createElementBlock("div", _hoisted_3$43, [..._cache[7] || (_cache[7] = [createBaseVNode("img", {
			src: "/su/assets/teralinkx2-D-ymN_3H.png",
			alt: "Logo",
			class: "h-10 w-10 object-contain"
		}, null, -1)])]))]),
		!$data.isCollapsed ? (openBlock(), createElementBlock("div", _hoisted_4$43, [createBaseVNode("div", _hoisted_5$43, [
			createBaseVNode("div", _hoisted_6$43, [_cache[8] || (_cache[8] = createBaseVNode("p", { class: "text-xs text-blue-600 dark:text-blue-400 font-medium" }, "Active Users", -1)), createBaseVNode("p", _hoisted_7$42, toDisplayString($props.stats.activeUsers), 1)]),
			createBaseVNode("div", _hoisted_8$40, [_cache[9] || (_cache[9] = createBaseVNode("p", { class: "text-xs text-emerald-600 dark:text-emerald-400 font-medium" }, "Sessions", -1)), createBaseVNode("p", _hoisted_9$38, toDisplayString($props.stats.activeSessions), 1)]),
			createBaseVNode("div", _hoisted_10$36, [_cache[10] || (_cache[10] = createBaseVNode("p", { class: "text-xs text-purple-600 dark:text-purple-400 font-medium" }, "Devices", -1)), createBaseVNode("p", _hoisted_11$31, toDisplayString($props.stats.activeDevices), 1)]),
			createBaseVNode("div", _hoisted_12$31, [_cache[11] || (_cache[11] = createBaseVNode("p", { class: "text-xs text-amber-600 dark:text-amber-400 font-medium" }, "Refunds", -1)), createBaseVNode("p", _hoisted_13$31, toDisplayString($props.stats.pendingRefunds), 1)])
		])])) : createCommentVNode("", true),
		createBaseVNode("nav", _hoisted_14$31, [createBaseVNode("div", _hoisted_15$31, [
			!$data.isCollapsed ? (openBlock(), createElementBlock("div", _hoisted_16$31, [..._cache[12] || (_cache[12] = [createBaseVNode("h3", { class: "text-xs font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wide" }, "Overview", -1)])])) : createCommentVNode("", true),
			(openBlock(true), createElementBlock(Fragment, null, renderList($data.overviewItems, (item) => {
				return openBlock(), createElementBlock("button", {
					key: item.id,
					onClick: ($event) => $options.selectComponent(item.component),
					title: $data.isCollapsed ? item.name : "",
					class: normalizeClass(["w-full flex items-center rounded-xl transition-all duration-200 text-left group text-sm relative overflow-hidden", [$data.isCollapsed ? "px-2 py-2.5 justify-center" : "px-3 py-2.5", $data.activeComponent === item.component ? "font-medium shadow-sm" : "hover:bg-slate-100 dark:hover:bg-slate-800"]]),
					style: normalizeStyle($data.activeComponent === item.component ? `background: ${item.color}; color: white;` : "")
				}, [createBaseVNode("span", {
					class: normalizeClass($data.isCollapsed ? "" : "mr-3"),
					innerHTML: item.icon,
					style: normalizeStyle($data.activeComponent === item.component ? "color: white;" : `color: ${item.color}`)
				}, null, 14, _hoisted_18$31), !$data.isCollapsed ? (openBlock(), createElementBlock("span", _hoisted_19$27, toDisplayString(item.name), 1)) : createCommentVNode("", true)], 14, _hoisted_17$31);
			}), 128)),
			!$data.isCollapsed ? (openBlock(), createElementBlock("div", _hoisted_20$27, [..._cache[13] || (_cache[13] = [createBaseVNode("h3", { class: "text-xs font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wide" }, "User Management", -1)])])) : (openBlock(), createElementBlock("div", _hoisted_21$26)),
			(openBlock(true), createElementBlock(Fragment, null, renderList($data.userManagementItems, (item) => {
				return openBlock(), createElementBlock("button", {
					key: item.id,
					onClick: ($event) => $options.selectComponent(item.component),
					title: $data.isCollapsed ? item.name : "",
					class: normalizeClass(["w-full flex items-center rounded-xl transition-all duration-200 text-left group text-sm relative overflow-hidden", [$data.isCollapsed ? "px-2 py-2.5 justify-center" : "px-3 py-2.5", $data.activeComponent === item.component ? "font-medium shadow-sm" : "hover:bg-slate-100 dark:hover:bg-slate-800"]]),
					style: normalizeStyle($data.activeComponent === item.component ? `background: ${item.color}; color: white;` : "")
				}, [
					createBaseVNode("span", {
						class: normalizeClass($data.isCollapsed ? "" : "mr-3"),
						innerHTML: item.icon,
						style: normalizeStyle($data.activeComponent === item.component ? "color: white;" : `color: ${item.color}`)
					}, null, 14, _hoisted_23$25),
					!$data.isCollapsed ? (openBlock(), createElementBlock("span", _hoisted_24$24, toDisplayString(item.name), 1)) : createCommentVNode("", true),
					!$data.isCollapsed && $options.getBadgeCount(item.component) > 0 ? (openBlock(), createElementBlock("span", {
						key: 1,
						class: "text-xs rounded-full px-2 py-0.5 min-w-5 text-center font-bold shadow-sm",
						style: normalizeStyle($data.activeComponent === item.component ? "background-color: white; color: " + item.color : `background-color: ${item.color}; color: white;`)
					}, toDisplayString($options.getBadgeCount(item.component)), 5)) : createCommentVNode("", true)
				], 14, _hoisted_22$26);
			}), 128)),
			!$data.isCollapsed ? (openBlock(), createElementBlock("div", _hoisted_25$24, [..._cache[14] || (_cache[14] = [createBaseVNode("h3", { class: "text-xs font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wide" }, "Products & Services", -1)])])) : (openBlock(), createElementBlock("div", _hoisted_26$24)),
			(openBlock(true), createElementBlock(Fragment, null, renderList($data.productsItems, (item) => {
				return openBlock(), createElementBlock("button", {
					key: item.id,
					onClick: ($event) => $options.selectComponent(item.component),
					title: $data.isCollapsed ? item.name : "",
					class: normalizeClass(["w-full flex items-center rounded-xl transition-all duration-200 text-left group text-sm relative overflow-hidden", [$data.isCollapsed ? "px-2 py-2.5 justify-center" : "px-3 py-2.5", $data.activeComponent === item.component ? "font-medium shadow-sm" : "hover:bg-slate-100 dark:hover:bg-slate-800"]]),
					style: normalizeStyle($data.activeComponent === item.component ? `background: ${item.color}; color: white;` : "")
				}, [createBaseVNode("span", {
					class: normalizeClass($data.isCollapsed ? "" : "mr-3"),
					innerHTML: item.icon,
					style: normalizeStyle($data.activeComponent === item.component ? "color: white;" : `color: ${item.color}`)
				}, null, 14, _hoisted_28$23), !$data.isCollapsed ? (openBlock(), createElementBlock("span", _hoisted_29$23, toDisplayString(item.name), 1)) : createCommentVNode("", true)], 14, _hoisted_27$23);
			}), 128)),
			!$data.isCollapsed ? (openBlock(), createElementBlock("div", _hoisted_30$22, [..._cache[15] || (_cache[15] = [createBaseVNode("h3", { class: "text-xs font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wide" }, "Financial", -1)])])) : (openBlock(), createElementBlock("div", _hoisted_31$21)),
			(openBlock(true), createElementBlock(Fragment, null, renderList($data.financialItems, (item) => {
				return openBlock(), createElementBlock("button", {
					key: item.id,
					onClick: ($event) => $options.selectComponent(item.component),
					title: $data.isCollapsed ? item.name : "",
					class: normalizeClass(["w-full flex items-center rounded-xl transition-all duration-200 text-left group text-sm relative overflow-hidden", [$data.isCollapsed ? "px-2 py-2.5 justify-center" : "px-3 py-2.5", $data.activeComponent === item.component ? "font-medium shadow-sm" : "hover:bg-slate-100 dark:hover:bg-slate-800"]]),
					style: normalizeStyle($data.activeComponent === item.component ? `background: ${item.color}; color: white;` : "")
				}, [
					createBaseVNode("span", {
						class: normalizeClass($data.isCollapsed ? "" : "mr-3"),
						innerHTML: item.icon,
						style: normalizeStyle($data.activeComponent === item.component ? "color: white;" : `color: ${item.color}`)
					}, null, 14, _hoisted_33$20),
					!$data.isCollapsed ? (openBlock(), createElementBlock("span", _hoisted_34$20, toDisplayString(item.name), 1)) : createCommentVNode("", true),
					!$data.isCollapsed && $options.getBadgeCount(item.component) > 0 ? (openBlock(), createElementBlock("span", {
						key: 1,
						class: "text-xs rounded-full px-2 py-0.5 min-w-5 text-center font-bold shadow-sm",
						style: normalizeStyle($data.activeComponent === item.component ? "background-color: white; color: " + item.color : `background-color: ${item.color}; color: white;`)
					}, toDisplayString($options.getBadgeCount(item.component)), 5)) : createCommentVNode("", true)
				], 14, _hoisted_32$20);
			}), 128)),
			!$data.isCollapsed ? (openBlock(), createElementBlock("div", _hoisted_35$19, [..._cache[16] || (_cache[16] = [createBaseVNode("h3", { class: "text-xs font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wide" }, "Network", -1)])])) : (openBlock(), createElementBlock("div", _hoisted_36$19)),
			(openBlock(true), createElementBlock(Fragment, null, renderList($data.networkItems, (item) => {
				return openBlock(), createElementBlock("button", {
					key: item.id,
					onClick: ($event) => $options.selectComponent(item.component),
					title: $data.isCollapsed ? item.name : "",
					class: normalizeClass(["w-full flex items-center rounded-xl transition-all duration-200 text-left group text-sm relative overflow-hidden", [$data.isCollapsed ? "px-2 py-2.5 justify-center" : "px-3 py-2.5", $data.activeComponent === item.component ? "font-medium shadow-sm" : "hover:bg-slate-100 dark:hover:bg-slate-800"]]),
					style: normalizeStyle($data.activeComponent === item.component ? `background: ${item.color}; color: white;` : "")
				}, [createBaseVNode("span", {
					class: normalizeClass($data.isCollapsed ? "" : "mr-3"),
					innerHTML: item.icon,
					style: normalizeStyle($data.activeComponent === item.component ? "color: white;" : `color: ${item.color}`)
				}, null, 14, _hoisted_38$19), !$data.isCollapsed ? (openBlock(), createElementBlock("span", _hoisted_39$19, toDisplayString(item.name), 1)) : createCommentVNode("", true)], 14, _hoisted_37$19);
			}), 128)),
			!$data.isCollapsed ? (openBlock(), createElementBlock("div", _hoisted_40$19, [..._cache[17] || (_cache[17] = [createBaseVNode("h3", { class: "text-xs font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wide" }, "Support", -1)])])) : (openBlock(), createElementBlock("div", _hoisted_41$18)),
			(openBlock(true), createElementBlock(Fragment, null, renderList($data.supportMenuItems, (item) => {
				return openBlock(), createElementBlock("button", {
					key: item.id,
					onClick: ($event) => $options.selectComponent(item.component),
					title: $data.isCollapsed ? item.name : "",
					class: normalizeClass(["w-full flex items-center rounded-xl transition-all duration-200 text-left group text-sm", [$data.isCollapsed ? "px-2 py-2.5 justify-center" : "px-3 py-2.5", $data.activeComponent === item.component ? "bg-gradient-to-r from-slate-500/10 to-slate-600/10 text-slate-700 dark:text-slate-300 font-medium shadow-sm" : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"]])
				}, [createBaseVNode("span", {
					class: normalizeClass($data.isCollapsed ? "" : "mr-3"),
					innerHTML: item.icon
				}, null, 10, _hoisted_43$15), !$data.isCollapsed ? (openBlock(), createElementBlock("span", _hoisted_44$15, toDisplayString(item.name), 1)) : createCommentVNode("", true)], 10, _hoisted_42$16);
			}), 128))
		])]),
		createBaseVNode("div", _hoisted_45$12, [createBaseVNode("button", {
			onClick: _cache[1] || (_cache[1] = (...args) => $options.toggleSidebar && $options.toggleSidebar(...args)),
			class: "w-full p-2 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors flex items-center justify-center text-slate-600 dark:text-slate-400 hidden lg:flex border-b border-slate-200 dark:border-slate-800"
		}, [(openBlock(), createElementBlock("svg", _hoisted_46$12, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: $data.isCollapsed ? "M13 5l7 7-7 7M5 5l7 7-7 7" : "M11 19l-7-7 7-7M19 19l-7-7 7-7"
		}, null, 8, _hoisted_47$11)]))]), createBaseVNode("div", _hoisted_48$8, [!$data.isCollapsed ? (openBlock(), createElementBlock("div", _hoisted_49$8, [createBaseVNode("div", _hoisted_50$8, [_cache[20] || (_cache[20] = createBaseVNode("span", { class: "text-xs font-semibold text-slate-700 dark:text-slate-300" }, "Theme", -1)), createBaseVNode("button", {
			onClick: _cache[2] || (_cache[2] = (...args) => $setup.toggleTheme && $setup.toggleTheme(...args)),
			class: "p-2 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700 transition-all shadow-md hover:shadow-lg"
		}, [$setup.isDark ? (openBlock(), createElementBlock("svg", _hoisted_51$8, [..._cache[18] || (_cache[18] = [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M12 3v1m0 16v1m8.66-12.66l-.71.71M4.05 19.95l-.7-.71M21 12h-1M4 12H3m16.95 7.05l-.7-.71M4.05 4.05l.7.71M16 12a4 4 0 11-8 0 4 4 0 018 0z"
		}, null, -1)])])) : (openBlock(), createElementBlock("svg", _hoisted_52$7, [..._cache[19] || (_cache[19] = [createBaseVNode("path", { d: "M10 2a8 8 0 106.32 12.906 7.5 7.5 0 01-6.32-12.905z" }, null, -1)])]))])]), createBaseVNode("label", _hoisted_53$7, [withDirectives(createBaseVNode("input", {
			type: "checkbox",
			"onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => $setup.isAuto = $event),
			onChange: _cache[4] || (_cache[4] = (...args) => $setup.handleAutoThemeChange && $setup.handleAutoThemeChange(...args)),
			class: "w-4 h-4 rounded border-slate-300 dark:border-slate-600 text-blue-600 focus:ring-blue-500 focus:ring-offset-0"
		}, null, 544), [[vModelCheckbox, $setup.isAuto]]), _cache[21] || (_cache[21] = createBaseVNode("span", { class: "ml-2 text-xs text-slate-600 dark:text-slate-400" }, "Auto (6AM-6PM)", -1))])])) : (openBlock(), createElementBlock("div", _hoisted_54$6, [createBaseVNode("button", {
			onClick: _cache[5] || (_cache[5] = (...args) => $setup.toggleTheme && $setup.toggleTheme(...args)),
			class: "p-2 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700 transition-all shadow-md hover:shadow-lg"
		}, [$setup.isDark ? (openBlock(), createElementBlock("svg", _hoisted_55$5, [..._cache[22] || (_cache[22] = [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M12 3v1m0 16v1m8.66-12.66l-.71.71M4.05 19.95l-.7-.71M21 12h-1M4 12H3m16.95 7.05l-.7-.71M4.05 4.05l.7.71M16 12a4 4 0 11-8 0 4 4 0 018 0z"
		}, null, -1)])])) : (openBlock(), createElementBlock("svg", _hoisted_56$4, [..._cache[23] || (_cache[23] = [createBaseVNode("path", { d: "M10 2a8 8 0 106.32 12.906 7.5 7.5 0 01-6.32-12.905z" }, null, -1)])]))])])), !$data.isCollapsed ? (openBlock(), createElementBlock("div", _hoisted_57$4, [..._cache[24] || (_cache[24] = [createBaseVNode("div", { class: "flex items-center" }, [createBaseVNode("div", { class: "w-1.5 h-1.5 bg-emerald-500 rounded-full mr-1.5 animate-pulse" }), createBaseVNode("span", { class: "text-slate-600 dark:text-slate-400" }, "Online")], -1), createBaseVNode("span", { class: "text-slate-500 dark:text-slate-500 font-mono" }, "v2.1.0", -1)])])) : (openBlock(), createElementBlock("div", _hoisted_58$4, [..._cache[25] || (_cache[25] = [createBaseVNode("div", { class: "w-2 h-2 bg-emerald-500 rounded-full animate-pulse" }, null, -1)])]))])])
	], 2)]);
}
var Sidebar_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$43, [["render", _sfc_render$43], ["__scopeId", "data-v-aafcc5d8"]]);
var import_pusher = /* @__PURE__ */ __toESM(require_pusher());
var pusherInstance = ref(null);
var isConnected = ref(false);
function usePusher() {
	const initPusher = (userId) => {
		if (pusherInstance.value) return pusherInstance.value;
		pusherInstance.value = new import_pusher.default("your_pusher_key", {
			cluster: "mt1",
			encrypted: true
		});
		pusherInstance.value.connection.bind("connected", () => {
			isConnected.value = true;
			console.log("✅ Pusher connected");
		});
		pusherInstance.value.connection.bind("disconnected", () => {
			isConnected.value = false;
			console.log("❌ Pusher disconnected");
		});
		return pusherInstance.value;
	};
	const subscribe = (channelName, eventName, callback) => {
		if (!pusherInstance.value) {
			console.error("Pusher not initialized");
			return null;
		}
		const channel = pusherInstance.value.subscribe(channelName);
		channel.bind(eventName, callback);
		return channel;
	};
	const unsubscribe = (channelName) => {
		if (pusherInstance.value) pusherInstance.value.unsubscribe(channelName);
	};
	const disconnect = () => {
		if (pusherInstance.value) {
			pusherInstance.value.disconnect();
			pusherInstance.value = null;
			isConnected.value = false;
		}
	};
	return {
		pusherInstance,
		isConnected,
		initPusher,
		subscribe,
		unsubscribe,
		disconnect
	};
}
var _sfc_main$42 = {
	name: "RealTimeNotifications",
	setup() {
		const { initPusher, subscribe, disconnect } = usePusher();
		const notifications = ref([]);
		let notificationId = 0;
		const addNotification = (data) => {
			const id = ++notificationId;
			notifications.value.push({
				id,
				message: data.message || "New notification",
				type: data.type || "info",
				details: data.details || null
			});
			setTimeout(() => {
				removeNotification(id);
			}, 5e3);
		};
		const removeNotification = (id) => {
			const index = notifications.value.findIndex((n) => n.id === id);
			if (index > -1) notifications.value.splice(index, 1);
		};
		onMounted(() => {
			const userId = localStorage.getItem("userId");
			if (userId) {
				initPusher(userId);
				subscribe("admin-notifications", "new-alert", (data) => {
					addNotification(data);
				});
				subscribe(`user-${userId}`, "new-alert", (data) => {
					addNotification(data);
				});
			}
		});
		onUnmounted(() => {
			disconnect();
		});
		return {
			notifications,
			removeNotification
		};
	}
};
var _hoisted_1$42 = { class: "fixed top-20 right-4 z-50 space-y-2 max-w-sm" };
var _hoisted_2$42 = { class: "flex-shrink-0" };
var _hoisted_3$42 = {
	key: 0,
	class: "w-6 h-6 text-emerald-500",
	fill: "currentColor",
	viewBox: "0 0 24 24"
};
var _hoisted_4$42 = {
	key: 1,
	class: "w-6 h-6 text-rose-500",
	fill: "currentColor",
	viewBox: "0 0 24 24"
};
var _hoisted_5$42 = {
	key: 2,
	class: "w-6 h-6 text-amber-500",
	fill: "currentColor",
	viewBox: "0 0 24 24"
};
var _hoisted_6$42 = {
	key: 3,
	class: "w-6 h-6 text-blue-500",
	fill: "currentColor",
	viewBox: "0 0 24 24"
};
var _hoisted_7$41 = { class: "flex-1 min-w-0" };
var _hoisted_8$39 = { class: "text-sm font-medium text-slate-900 dark:text-white" };
var _hoisted_9$37 = {
	key: 0,
	class: "text-xs text-slate-500 dark:text-slate-400 mt-1"
};
var _hoisted_10$35 = ["onClick"];
function _sfc_render$42(_ctx, _cache, $props, $setup, $data, $options) {
	return openBlock(), createElementBlock("div", _hoisted_1$42, [createVNode(TransitionGroup, { name: "notification" }, {
		default: withCtx(() => [(openBlock(true), createElementBlock(Fragment, null, renderList($setup.notifications, (notification) => {
			return openBlock(), createElementBlock("div", {
				key: notification.id,
				class: "bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 p-4 flex items-start gap-3"
			}, [
				createBaseVNode("div", _hoisted_2$42, [notification.type === "success" ? (openBlock(), createElementBlock("svg", _hoisted_3$42, [..._cache[0] || (_cache[0] = [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" }, null, -1)])])) : notification.type === "error" ? (openBlock(), createElementBlock("svg", _hoisted_4$42, [..._cache[1] || (_cache[1] = [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" }, null, -1)])])) : notification.type === "warning" ? (openBlock(), createElementBlock("svg", _hoisted_5$42, [..._cache[2] || (_cache[2] = [createBaseVNode("path", { d: "M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z" }, null, -1)])])) : (openBlock(), createElementBlock("svg", _hoisted_6$42, [..._cache[3] || (_cache[3] = [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z" }, null, -1)])]))]),
				createBaseVNode("div", _hoisted_7$41, [createBaseVNode("p", _hoisted_8$39, toDisplayString(notification.message), 1), notification.details ? (openBlock(), createElementBlock("p", _hoisted_9$37, toDisplayString(notification.details), 1)) : createCommentVNode("", true)]),
				createBaseVNode("button", {
					onClick: ($event) => $setup.removeNotification(notification.id),
					class: "flex-shrink-0 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
				}, [..._cache[4] || (_cache[4] = [createBaseVNode("svg", {
					class: "w-5 h-5",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" })], -1)])], 8, _hoisted_10$35)
			]);
		}), 128))]),
		_: 1
	})]);
}
var RealTimeNotifications_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$42, [["render", _sfc_render$42], ["__scopeId", "data-v-e194a8ed"]]);
var _sfc_main$41 = {
	name: "ModernMetricCard",
	components: { TrendIcon: {
		name: "TrendIcon",
		props: { trend: {
			type: String,
			default: "stable",
			validator: (val) => [
				"up",
				"down",
				"stable"
			].includes(val)
		} },
		render() {
			if (this.trend === "up") return h("svg", {
				class: "w-4 h-4 text-emerald-600",
				fill: "none",
				viewBox: "0 0 24 24",
				stroke: "currentColor"
			}, [h("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M5 10l7-7m0 0l7 7m-7-7v18"
			})]);
			else if (this.trend === "down") return h("svg", {
				class: "w-4 h-4 text-rose-600",
				fill: "none",
				viewBox: "0 0 24 24",
				stroke: "currentColor"
			}, [h("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M19 14l-7 7m0 0l-7-7m7 7V3"
			})]);
			else return h("svg", {
				class: "w-4 h-4 text-slate-600",
				fill: "none",
				viewBox: "0 0 24 24",
				stroke: "currentColor"
			}, [h("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M5 12h14"
			})]);
		}
	} },
	props: {
		title: {
			type: String,
			required: true
		},
		value: {
			type: [String, Number],
			required: true
		},
		trend: {
			type: String,
			validator: (val) => [
				"up",
				"down",
				"stable"
			].includes(val),
			default: "stable"
		},
		trendValue: {
			type: String,
			default: "0%"
		},
		color: {
			type: String,
			default: "blue",
			validator: (val) => [
				"blue",
				"emerald",
				"green",
				"purple",
				"amber",
				"indigo",
				"cyan",
				"rose"
			].includes(val)
		},
		formatted: {
			type: Boolean,
			default: true
		}
	},
	computed: {
		formattedValue() {
			if (this.value === void 0 || this.value === null) return "0";
			if (!this.formatted || typeof this.value !== "number") return this.value;
			return new Intl.NumberFormat().format(this.value);
		},
		valueSize() {
			const length = String(this.formattedValue || "0").length;
			if (length > 12) return "text-lg";
			if (length > 8) return "text-xl";
			return "text-2xl";
		},
		iconBgColor() {
			const colors = {
				blue: "bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400",
				emerald: "bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
				green: "bg-green-50 dark:bg-green-500/10 text-green-600 dark:text-green-400",
				purple: "bg-purple-50 dark:bg-purple-500/10 text-purple-600 dark:text-purple-400",
				amber: "bg-amber-50 dark:bg-amber-500/10 text-amber-600 dark:text-amber-400",
				indigo: "bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400",
				cyan: "bg-cyan-50 dark:bg-cyan-500/10 text-cyan-600 dark:text-cyan-400",
				rose: "bg-rose-50 dark:bg-rose-500/10 text-rose-600 dark:text-rose-400"
			};
			return colors[this.color] || colors.blue;
		},
		trendTextColor() {
			return {
				up: "text-emerald-600 dark:text-emerald-400",
				down: "text-rose-600 dark:text-rose-400",
				stable: "text-slate-600 dark:text-slate-400"
			}[this.trend];
		}
	}
};
var _hoisted_1$41 = { class: "group" };
var _hoisted_2$41 = { class: "bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600 transition-all duration-200 hover:shadow-md" };
var _hoisted_3$41 = { class: "flex items-center justify-between mb-4" };
var _hoisted_4$41 = { class: "text-slate-600 dark:text-slate-400 font-medium text-sm" };
var _hoisted_5$41 = { class: "mb-3" };
var _hoisted_6$41 = { class: "flex items-center space-x-2" };
var _hoisted_7$40 = { class: "text-xs font-medium" };
function _sfc_render$41(_ctx, _cache, $props, $setup, $data, $options) {
	const _component_TrendIcon = resolveComponent("TrendIcon");
	return openBlock(), createElementBlock("div", _hoisted_1$41, [createBaseVNode("div", _hoisted_2$41, [
		createBaseVNode("div", _hoisted_3$41, [createBaseVNode("h3", _hoisted_4$41, toDisplayString($props.title), 1), createBaseVNode("div", { class: normalizeClass(["w-9 h-9 rounded-lg flex items-center justify-center", $options.iconBgColor]) }, [renderSlot(_ctx.$slots, "default")], 2)]),
		createBaseVNode("div", _hoisted_5$41, [createBaseVNode("div", { class: normalizeClass(["font-semibold text-slate-900 dark:text-white", $options.valueSize]) }, toDisplayString($options.formattedValue), 3)]),
		createBaseVNode("div", _hoisted_6$41, [createBaseVNode("div", { class: normalizeClass(["flex items-center space-x-1", $options.trendTextColor]) }, [createVNode(_component_TrendIcon, { trend: $props.trend }, null, 8, ["trend"]), createBaseVNode("span", _hoisted_7$40, toDisplayString($props.trendValue), 1)], 2), _cache[0] || (_cache[0] = createBaseVNode("span", { class: "text-slate-400 dark:text-slate-500 text-xs" }, "vs last week", -1))])
	])]);
}
var MetricCard_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$41, [["render", _sfc_render$41]]);
var PRIMARY_URL = "https://srv.teralinkxwaves.uk";
var FALLBACK_URL = "https://accounts.teralinkxwaves.uk";
var activeBaseURL = PRIMARY_URL;
var primaryFailed = false;
function createHttp(baseURL) {
	return axios_default.create({
		baseURL,
		timeout: 15e3,
		headers: {
			"Content-Type": "application/json",
			"X-Requested-With": "XMLHttpRequest"
		},
		withCredentials: true
	});
}
var http = createHttp(PRIMARY_URL);
var testPrimaryServer = async () => {
	try {
		await axios_default.get(`${PRIMARY_URL}/api/health/`, { timeout: 2e3 });
		console.log("[API] Primary server is reachable:", PRIMARY_URL);
	} catch (error) {
		console.warn("[API] Primary server unreachable on startup, switching to fallback:", FALLBACK_URL);
		primaryFailed = true;
		activeBaseURL = FALLBACK_URL;
		http.defaults.baseURL = FALLBACK_URL;
	}
};
testPrimaryServer();
http.interceptors.request.use((config) => {
	const token = localStorage.getItem("access_token");
	if (token) config.headers.Authorization = `Bearer ${token}`;
	const csrf = getCookie("csrftoken");
	if (csrf) config.headers["X-CSRFToken"] = csrf;
	return config;
}, (error) => Promise.reject(error));
http.interceptors.response.use((response) => {
	if (primaryFailed) {
		primaryFailed = false;
		activeBaseURL = PRIMARY_URL;
		http.defaults.baseURL = PRIMARY_URL;
		console.log("[API] Primary server restored:", PRIMARY_URL);
	}
	return response;
}, async (error) => {
	const isNetworkError = !error.response;
	const isServerError = error.response?.status >= 500;
	const alreadyFallback = error.config?.baseURL === FALLBACK_URL;
	if ((isNetworkError || isServerError) && !alreadyFallback && !primaryFailed) {
		console.warn(`[API] Primary ${PRIMARY_URL} unreachable, falling back to ${FALLBACK_URL}`);
		primaryFailed = true;
		activeBaseURL = FALLBACK_URL;
		http.defaults.baseURL = FALLBACK_URL;
		return axios_default({
			...error.config,
			baseURL: FALLBACK_URL
		});
	}
	if (error.response?.status === 401) {
		localStorage.removeItem("access_token");
		localStorage.removeItem("refresh_token");
		localStorage.removeItem("user");
		window.location.href = "/su/login";
		return Promise.reject(error);
	}
	return Promise.reject(error);
});
var cache = /* @__PURE__ */ new Map();
var CACHE_DURATION = 6e4;
function getCookie(name) {
	if (!document.cookie) return null;
	const match = document.cookie.split(";").map((c) => c.trim()).find((c) => c.startsWith(name + "="));
	return match ? decodeURIComponent(match.split("=")[1]) : null;
}
function useApi() {
	const loading = ref(false);
	const error = ref(null);
	const makeRequest = async (method, url, data = null, useCache = true) => {
		const cacheKey = `${method}:${url}:${JSON.stringify(data)}`;
		if (method === "get" && useCache) {
			const cached = cache.get(cacheKey);
			if (cached && Date.now() - cached.timestamp < CACHE_DURATION) return cached.data;
		}
		loading.value = true;
		error.value = null;
		try {
			const response = await http({
				method,
				url,
				data
			});
			if (method === "get" && useCache) {
				cache.set(cacheKey, {
					data: response.data,
					timestamp: Date.now()
				});
				if (cache.size > 100) cache.delete(cache.keys().next().value);
			}
			return response.data;
		} catch (err) {
			error.value = err.response?.data?.error || err.response?.data?.message || err.message;
			throw err;
		} finally {
			loading.value = false;
		}
	};
	const clearCache = () => cache.clear();
	const getActiveURL = () => activeBaseURL;
	return {
		loading,
		error,
		makeRequest,
		clearCache,
		getActiveURL
	};
}
var _sfc_main$40 = {
	name: "DateRangePicker",
	emits: ["change"],
	data() {
		return {
			showPicker: false,
			selectedPreset: "last7days",
			customStart: "",
			customEnd: "",
			compareEnabled: false,
			presets: [
				{
					label: "Today",
					value: "today"
				},
				{
					label: "Yesterday",
					value: "yesterday"
				},
				{
					label: "Last 7 Days",
					value: "last7days"
				},
				{
					label: "Last 30 Days",
					value: "last30days"
				},
				{
					label: "This Month",
					value: "thismonth"
				},
				{
					label: "Last Month",
					value: "lastmonth"
				},
				{
					label: "Last 90 Days",
					value: "last90days"
				},
				{
					label: "This Year",
					value: "thisyear"
				}
			]
		};
	},
	computed: { displayText() {
		const preset = this.presets.find((p) => p.value === this.selectedPreset);
		if (preset) return preset.label;
		if (this.customStart && this.customEnd) return `${this.customStart} - ${this.customEnd}`;
		return "Select Date Range";
	} },
	methods: {
		selectPreset(preset) {
			this.selectedPreset = preset.value;
			const { start, end } = this.getPresetDates(preset.value);
			this.customStart = start;
			this.customEnd = end;
		},
		getPresetDates(preset) {
			const today = /* @__PURE__ */ new Date();
			const formatDate = (date) => date.toISOString().split("T")[0];
			switch (preset) {
				case "today": return {
					start: formatDate(today),
					end: formatDate(today)
				};
				case "yesterday":
					const yesterday = new Date(today);
					yesterday.setDate(yesterday.getDate() - 1);
					return {
						start: formatDate(yesterday),
						end: formatDate(yesterday)
					};
				case "last7days":
					const week = new Date(today);
					week.setDate(week.getDate() - 7);
					return {
						start: formatDate(week),
						end: formatDate(today)
					};
				case "last30days":
					const month = new Date(today);
					month.setDate(month.getDate() - 30);
					return {
						start: formatDate(month),
						end: formatDate(today)
					};
				case "last90days":
					const quarter = new Date(today);
					quarter.setDate(quarter.getDate() - 90);
					return {
						start: formatDate(quarter),
						end: formatDate(today)
					};
				case "thismonth": return {
					start: formatDate(new Date(today.getFullYear(), today.getMonth(), 1)),
					end: formatDate(today)
				};
				case "lastmonth":
					const lastMonthStart = new Date(today.getFullYear(), today.getMonth() - 1, 1);
					const lastMonthEnd = new Date(today.getFullYear(), today.getMonth(), 0);
					return {
						start: formatDate(lastMonthStart),
						end: formatDate(lastMonthEnd)
					};
				case "thisyear": return {
					start: formatDate(new Date(today.getFullYear(), 0, 1)),
					end: formatDate(today)
				};
				default: return {
					start: formatDate(today),
					end: formatDate(today)
				};
			}
		},
		applyRange() {
			this.$emit("change", {
				start: this.customStart,
				end: this.customEnd,
				compare: this.compareEnabled,
				preset: this.selectedPreset
			});
			this.showPicker = false;
		}
	},
	mounted() {
		this.selectPreset(this.presets[2]);
	}
};
var _hoisted_1$40 = { class: "relative" };
var _hoisted_2$40 = { class: "text-slate-900 dark:text-white" };
var _hoisted_3$40 = {
	key: 0,
	class: "absolute top-full mt-2 right-0 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-xl z-50 w-80"
};
var _hoisted_4$40 = { class: "p-4 space-y-3" };
var _hoisted_5$40 = { class: "grid grid-cols-2 gap-2" };
var _hoisted_6$40 = ["onClick"];
var _hoisted_7$39 = { class: "pt-3 border-t border-slate-200 dark:border-slate-700 space-y-2" };
var _hoisted_8$38 = { class: "pt-3 border-t border-slate-200 dark:border-slate-700" };
var _hoisted_9$36 = { class: "flex items-center gap-2 cursor-pointer" };
var _hoisted_10$34 = { class: "flex gap-2 pt-3 border-t border-slate-200 dark:border-slate-700" };
function _sfc_render$40(_ctx, _cache, $props, $setup, $data, $options) {
	return openBlock(), createElementBlock("div", _hoisted_1$40, [createBaseVNode("button", {
		onClick: _cache[0] || (_cache[0] = ($event) => $data.showPicker = !$data.showPicker),
		class: "flex items-center gap-2 px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg hover:border-slate-300 dark:hover:border-slate-600 transition-colors text-sm"
	}, [
		_cache[6] || (_cache[6] = createBaseVNode("svg", {
			class: "w-4 h-4 text-slate-600 dark:text-slate-400",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
		})], -1)),
		createBaseVNode("span", _hoisted_2$40, toDisplayString($options.displayText), 1),
		_cache[7] || (_cache[7] = createBaseVNode("svg", {
			class: "w-4 h-4 text-slate-400",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M19 9l-7 7-7-7"
		})], -1))
	]), $data.showPicker ? (openBlock(), createElementBlock("div", _hoisted_3$40, [createBaseVNode("div", _hoisted_4$40, [
		createBaseVNode("div", _hoisted_5$40, [(openBlock(true), createElementBlock(Fragment, null, renderList($data.presets, (preset) => {
			return openBlock(), createElementBlock("button", {
				key: preset.value,
				onClick: ($event) => $options.selectPreset(preset),
				class: normalizeClass(["px-3 py-2 text-xs rounded-lg transition-colors", $data.selectedPreset === preset.value ? "bg-blue-500 text-white" : "bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-white hover:bg-slate-200 dark:hover:bg-slate-600"])
			}, toDisplayString(preset.label), 11, _hoisted_6$40);
		}), 128))]),
		createBaseVNode("div", _hoisted_7$39, [createBaseVNode("div", null, [_cache[8] || (_cache[8] = createBaseVNode("label", { class: "text-xs text-slate-600 dark:text-slate-400 mb-1 block" }, "Start Date", -1)), withDirectives(createBaseVNode("input", {
			"onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => $data.customStart = $event),
			type: "date",
			class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
		}, null, 512), [[vModelText, $data.customStart]])]), createBaseVNode("div", null, [_cache[9] || (_cache[9] = createBaseVNode("label", { class: "text-xs text-slate-600 dark:text-slate-400 mb-1 block" }, "End Date", -1)), withDirectives(createBaseVNode("input", {
			"onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => $data.customEnd = $event),
			type: "date",
			class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
		}, null, 512), [[vModelText, $data.customEnd]])])]),
		createBaseVNode("div", _hoisted_8$38, [createBaseVNode("label", _hoisted_9$36, [withDirectives(createBaseVNode("input", {
			"onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => $data.compareEnabled = $event),
			type: "checkbox",
			class: "w-4 h-4 text-blue-600 rounded"
		}, null, 512), [[vModelCheckbox, $data.compareEnabled]]), _cache[10] || (_cache[10] = createBaseVNode("span", { class: "text-xs text-slate-900 dark:text-white" }, "Compare with previous period", -1))])]),
		createBaseVNode("div", _hoisted_10$34, [createBaseVNode("button", {
			onClick: _cache[4] || (_cache[4] = (...args) => $options.applyRange && $options.applyRange(...args)),
			class: "flex-1 px-3 py-2 bg-blue-500 hover:bg-blue-600 text-white text-xs rounded-lg transition-colors"
		}, " Apply "), createBaseVNode("button", {
			onClick: _cache[5] || (_cache[5] = ($event) => $data.showPicker = false),
			class: "px-3 py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-900 dark:text-white text-xs rounded-lg transition-colors"
		}, " Cancel ")])
	])])) : createCommentVNode("", true)]);
}
var DateRangePicker_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$40, [["render", _sfc_render$40]]);
var _sfc_main$39 = {
	name: "MultiSelectFilter",
	props: {
		label: {
			type: String,
			default: "Filter"
		},
		options: {
			type: Array,
			required: true
		}
	},
	emits: ["change"],
	data() {
		return {
			showDropdown: false,
			selected: [],
			searchQuery: ""
		};
	},
	computed: {
		displayText() {
			if (this.selected.length === 0) return this.label;
			if (this.selected.length === 1) {
				const option = this.options.find((o) => o.value === this.selected[0]);
				return option ? option.label : this.label;
			}
			return `${this.selected.length} selected`;
		},
		selectedCount() {
			return this.selected.length;
		},
		filteredOptions() {
			if (!this.searchQuery) return this.options;
			const query = this.searchQuery.toLowerCase();
			return this.options.filter((o) => o.label.toLowerCase().includes(query));
		}
	},
	methods: {
		clearAll() {
			this.selected = [];
		},
		applyFilters() {
			this.$emit("change", this.selected);
			this.showDropdown = false;
		}
	}
};
var _hoisted_1$39 = { class: "relative" };
var _hoisted_2$39 = { class: "text-slate-900 dark:text-white" };
var _hoisted_3$39 = {
	key: 0,
	class: "px-2 py-0.5 bg-blue-500 text-white text-xs rounded-full"
};
var _hoisted_4$39 = {
	key: 0,
	class: "absolute top-full mt-2 right-0 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-xl z-50 w-72"
};
var _hoisted_5$39 = { class: "p-4 space-y-3" };
var _hoisted_6$39 = { class: "max-h-64 overflow-y-auto space-y-1" };
var _hoisted_7$38 = ["value"];
var _hoisted_8$37 = { class: "text-sm text-slate-900 dark:text-white" };
var _hoisted_9$35 = {
	key: 0,
	class: "text-center text-slate-400 text-xs py-4"
};
var _hoisted_10$33 = { class: "flex gap-2 pt-3 border-t border-slate-200 dark:border-slate-700" };
function _sfc_render$39(_ctx, _cache, $props, $setup, $data, $options) {
	return openBlock(), createElementBlock("div", _hoisted_1$39, [createBaseVNode("button", {
		onClick: _cache[0] || (_cache[0] = ($event) => $data.showDropdown = !$data.showDropdown),
		class: "flex items-center gap-2 px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg hover:border-slate-300 dark:hover:border-slate-600 transition-colors text-sm"
	}, [
		_cache[5] || (_cache[5] = createBaseVNode("svg", {
			class: "w-4 h-4 text-slate-600 dark:text-slate-400",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
		})], -1)),
		createBaseVNode("span", _hoisted_2$39, toDisplayString($options.displayText), 1),
		$options.selectedCount > 0 ? (openBlock(), createElementBlock("span", _hoisted_3$39, toDisplayString($options.selectedCount), 1)) : createCommentVNode("", true),
		_cache[6] || (_cache[6] = createBaseVNode("svg", {
			class: "w-4 h-4 text-slate-400",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M19 9l-7 7-7-7"
		})], -1))
	]), $data.showDropdown ? (openBlock(), createElementBlock("div", _hoisted_4$39, [createBaseVNode("div", _hoisted_5$39, [
		withDirectives(createBaseVNode("input", {
			"onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => $data.searchQuery = $event),
			type: "text",
			placeholder: "Search...",
			class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
		}, null, 512), [[vModelText, $data.searchQuery]]),
		createBaseVNode("div", _hoisted_6$39, [(openBlock(true), createElementBlock(Fragment, null, renderList($options.filteredOptions, (option) => {
			return openBlock(), createElementBlock("label", {
				key: option.value,
				class: "flex items-center gap-2 px-3 py-2 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-lg cursor-pointer"
			}, [withDirectives(createBaseVNode("input", {
				"onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => $data.selected = $event),
				value: option.value,
				type: "checkbox",
				class: "w-4 h-4 text-blue-600 rounded"
			}, null, 8, _hoisted_7$38), [[vModelCheckbox, $data.selected]]), createBaseVNode("span", _hoisted_8$37, toDisplayString(option.label), 1)]);
		}), 128)), $options.filteredOptions.length === 0 ? (openBlock(), createElementBlock("div", _hoisted_9$35, " No results found ")) : createCommentVNode("", true)]),
		createBaseVNode("div", _hoisted_10$33, [createBaseVNode("button", {
			onClick: _cache[3] || (_cache[3] = (...args) => $options.clearAll && $options.clearAll(...args)),
			class: "flex-1 px-3 py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-900 dark:text-white text-xs rounded-lg transition-colors"
		}, " Clear All "), createBaseVNode("button", {
			onClick: _cache[4] || (_cache[4] = (...args) => $options.applyFilters && $options.applyFilters(...args)),
			class: "flex-1 px-3 py-2 bg-blue-500 hover:bg-blue-600 text-white text-xs rounded-lg transition-colors"
		}, " Apply ")])
	])])) : createCommentVNode("", true)]);
}
var MultiSelectFilter_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$39, [["render", _sfc_render$39]]);
var _sfc_main$38 = {
	name: "ExportButton",
	props: {
		data: {
			type: [Array, Object],
			required: true
		},
		filename: {
			type: String,
			default: "export"
		}
	},
	data() {
		return {
			showMenu: false,
			loading: false
		};
	},
	methods: {
		async exportData(format) {
			this.loading = true;
			this.showMenu = false;
			try {
				if (format === "csv") this.exportCSV();
				else if (format === "excel") this.exportExcel();
				else if (format === "pdf") this.exportPDF();
			} catch (error) {
				console.error("Export error:", error);
				alert("Export failed. Please try again.");
			} finally {
				this.loading = false;
			}
		},
		exportCSV() {
			const data = Array.isArray(this.data) ? this.data : [this.data];
			if (data.length === 0) return;
			const headers = Object.keys(data[0]);
			const csv = [headers.join(","), ...data.map((row) => headers.map((h$1) => JSON.stringify(row[h$1] || "")).join(","))].join("\n");
			this.downloadFile(csv, `${this.filename}.csv`, "text/csv");
		},
		exportExcel() {
			const data = Array.isArray(this.data) ? this.data : [this.data];
			if (data.length === 0) return;
			const headers = Object.keys(data[0]);
			const csv = [headers.join(","), ...data.map((row) => headers.map((h$1) => JSON.stringify(row[h$1] || "")).join(","))].join("\n");
			this.downloadFile(csv, `${this.filename}.xlsx`, "application/vnd.ms-excel");
		},
		exportPDF() {
			const data = Array.isArray(this.data) ? this.data : [this.data];
			const content = JSON.stringify(data, null, 2);
			this.downloadFile(content, `${this.filename}.pdf`, "application/pdf");
		},
		downloadFile(content, filename, mimeType) {
			const blob = new Blob([content], { type: mimeType });
			const url = window.URL.createObjectURL(blob);
			const link = document.createElement("a");
			link.href = url;
			link.download = filename;
			document.body.appendChild(link);
			link.click();
			document.body.removeChild(link);
			window.URL.revokeObjectURL(url);
		}
	}
};
var _hoisted_1$38 = { class: "relative" };
var _hoisted_2$38 = ["disabled"];
var _hoisted_3$38 = {
	key: 0,
	class: "w-4 h-4",
	fill: "none",
	stroke: "currentColor",
	viewBox: "0 0 24 24"
};
var _hoisted_4$38 = {
	key: 1,
	class: "w-4 h-4 animate-spin",
	fill: "none",
	viewBox: "0 0 24 24"
};
var _hoisted_5$38 = {
	key: 0,
	class: "absolute top-full mt-2 right-0 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-xl z-50 w-48"
};
var _hoisted_6$38 = { class: "py-2" };
function _sfc_render$38(_ctx, _cache, $props, $setup, $data, $options) {
	return openBlock(), createElementBlock("div", _hoisted_1$38, [createBaseVNode("button", {
		onClick: _cache[0] || (_cache[0] = ($event) => $data.showMenu = !$data.showMenu),
		class: "flex items-center gap-2 px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg transition-colors text-sm",
		disabled: $data.loading
	}, [!$data.loading ? (openBlock(), createElementBlock("svg", _hoisted_3$38, [..._cache[4] || (_cache[4] = [createBaseVNode("path", {
		"stroke-linecap": "round",
		"stroke-linejoin": "round",
		"stroke-width": "2",
		d: "M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
	}, null, -1)])])) : (openBlock(), createElementBlock("svg", _hoisted_4$38, [..._cache[5] || (_cache[5] = [createBaseVNode("circle", {
		class: "opacity-25",
		cx: "12",
		cy: "12",
		r: "10",
		stroke: "currentColor",
		"stroke-width": "4"
	}, null, -1), createBaseVNode("path", {
		class: "opacity-75",
		fill: "currentColor",
		d: "M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
	}, null, -1)])])), _cache[6] || (_cache[6] = createBaseVNode("span", null, "Export", -1))], 8, _hoisted_2$38), $data.showMenu ? (openBlock(), createElementBlock("div", _hoisted_5$38, [createBaseVNode("div", _hoisted_6$38, [
		createBaseVNode("button", {
			onClick: _cache[1] || (_cache[1] = ($event) => $options.exportData("csv")),
			class: "w-full px-4 py-2 text-left text-sm text-slate-900 dark:text-white hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors flex items-center gap-3"
		}, [..._cache[7] || (_cache[7] = [createBaseVNode("svg", {
			class: "w-4 h-4 text-emerald-500",
			fill: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", { d: "M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z" })], -1), createBaseVNode("span", null, "Export as CSV", -1)])]),
		createBaseVNode("button", {
			onClick: _cache[2] || (_cache[2] = ($event) => $options.exportData("excel")),
			class: "w-full px-4 py-2 text-left text-sm text-slate-900 dark:text-white hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors flex items-center gap-3"
		}, [..._cache[8] || (_cache[8] = [createBaseVNode("svg", {
			class: "w-4 h-4 text-green-600",
			fill: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", { d: "M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z" })], -1), createBaseVNode("span", null, "Export as Excel", -1)])]),
		createBaseVNode("button", {
			onClick: _cache[3] || (_cache[3] = ($event) => $options.exportData("pdf")),
			class: "w-full px-4 py-2 text-left text-sm text-slate-900 dark:text-white hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors flex items-center gap-3"
		}, [..._cache[9] || (_cache[9] = [createBaseVNode("svg", {
			class: "w-4 h-4 text-red-500",
			fill: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", { d: "M20 2H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-8.5 7.5c0 .83-.67 1.5-1.5 1.5H9v2H7.5V7H10c.83 0 1.5.67 1.5 1.5v1zm5 2c0 .83-.67 1.5-1.5 1.5h-2.5V7H15c.83 0 1.5.67 1.5 1.5v3zm4-3H19v1h1.5V11H19v2h-1.5V7h3v1.5zM9 9.5h1v-1H9v1zM4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm10 5.5h1v-3h-1v3z" })], -1), createBaseVNode("span", null, "Export as PDF", -1)])])
	])])) : createCommentVNode("", true)]);
}
var ExportButton_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$38, [["render", _sfc_render$38]]);
var _sfc_main$37 = {
	name: "RealTimeMonitor",
	setup() {
		const { makeRequest } = useApi();
		return { makeRequest };
	},
	data() {
		return {
			todayRevenue: 0,
			todayTransactions: 0,
			onlineUsers: 0,
			activeSessions: 0,
			avgResponseTime: 0,
			updateInterval: null
		};
	},
	computed: { responseStatus() {
		return this.avgResponseTime < 200 ? "good" : "normal";
	} },
	mounted() {
		this.fetchRealTimeData();
		this.updateInterval = setInterval(() => {
			this.fetchRealTimeData();
		}, 5e3);
	},
	beforeUnmount() {
		if (this.updateInterval) clearInterval(this.updateInterval);
	},
	methods: {
		async fetchRealTimeData() {
			try {
				const startTime = Date.now();
				const metrics = await this.makeRequest("get", "suapi/dashboard-metrics/", null, true);
				this.todayRevenue = metrics.totalRevenue || 0;
				this.todayTransactions = metrics.totalPackagesSold || 0;
				this.onlineUsers = metrics.activeUsers || 0;
				this.activeSessions = metrics.activeUsers || 0;
				this.avgResponseTime = Math.round(Date.now() - startTime);
			} catch (error) {}
		},
		formatNumber(num) {
			return new Intl.NumberFormat().format(Math.round(num));
		}
	}
};
var _hoisted_1$37 = { class: "bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl p-6 text-white shadow-lg" };
var _hoisted_2$37 = { class: "grid grid-cols-1 md:grid-cols-3 gap-4" };
var _hoisted_3$37 = { class: "bg-white/10 backdrop-blur-sm rounded-lg p-4" };
var _hoisted_4$37 = { class: "text-3xl font-bold" };
var _hoisted_5$37 = { class: "text-xs opacity-75 mt-1" };
var _hoisted_6$37 = { class: "bg-white/10 backdrop-blur-sm rounded-lg p-4" };
var _hoisted_7$37 = { class: "text-3xl font-bold" };
var _hoisted_8$36 = { class: "text-xs opacity-75 mt-1" };
var _hoisted_9$34 = { class: "bg-white/10 backdrop-blur-sm rounded-lg p-4" };
var _hoisted_10$32 = { class: "text-3xl font-bold" };
function _sfc_render$37(_ctx, _cache, $props, $setup, $data, $options) {
	return openBlock(), createElementBlock("div", _hoisted_1$37, [_cache[3] || (_cache[3] = createBaseVNode("div", { class: "flex items-center justify-between mb-4" }, [createBaseVNode("h2", { class: "text-lg font-semibold flex items-center gap-2" }, [createBaseVNode("div", { class: "w-2 h-2 bg-white rounded-full animate-pulse" }), createTextVNode(" Real-Time Monitor ")]), createBaseVNode("span", { class: "text-xs opacity-75" }, "Updates every 5s")], -1)), createBaseVNode("div", _hoisted_2$37, [
		createBaseVNode("div", _hoisted_3$37, [
			_cache[0] || (_cache[0] = createBaseVNode("div", { class: "flex items-center gap-2 mb-2" }, [createBaseVNode("svg", {
				class: "w-5 h-5",
				fill: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", { d: "M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z" })]), createBaseVNode("span", { class: "text-sm opacity-90" }, "Today's Revenue")], -1)),
			createBaseVNode("p", _hoisted_4$37, "KSh " + toDisplayString($options.formatNumber($data.todayRevenue)), 1),
			createBaseVNode("p", _hoisted_5$37, toDisplayString($data.todayTransactions) + " transactions", 1)
		]),
		createBaseVNode("div", _hoisted_6$37, [
			_cache[1] || (_cache[1] = createBaseVNode("div", { class: "flex items-center gap-2 mb-2" }, [createBaseVNode("svg", {
				class: "w-5 h-5",
				fill: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", { d: "M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z" })]), createBaseVNode("span", { class: "text-sm opacity-90" }, "Online Users")], -1)),
			createBaseVNode("p", _hoisted_7$37, toDisplayString($data.onlineUsers), 1),
			createBaseVNode("p", _hoisted_8$36, toDisplayString($data.activeSessions) + " active sessions", 1)
		]),
		createBaseVNode("div", _hoisted_9$34, [
			_cache[2] || (_cache[2] = createBaseVNode("div", { class: "flex items-center gap-2 mb-2" }, [createBaseVNode("svg", {
				class: "w-5 h-5",
				fill: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", { d: "M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z" })]), createBaseVNode("span", { class: "text-sm opacity-90" }, "Avg Response")], -1)),
			createBaseVNode("p", _hoisted_10$32, toDisplayString($data.avgResponseTime) + "ms", 1),
			createBaseVNode("p", { class: normalizeClass(["text-xs opacity-75 mt-1", $options.responseStatus === "good" ? "text-emerald-200" : "text-amber-200"]) }, toDisplayString($options.responseStatus === "good" ? "Excellent" : "Normal"), 3)
		])
	])]);
}
var _sfc_main$36 = {
	name: "Dashboard",
	components: {
		ModernMetricCard: MetricCard_default,
		apexchart: m,
		DateRangePicker: DateRangePicker_default,
		MultiSelectFilter: MultiSelectFilter_default,
		ExportButton: ExportButton_default,
		RealTimeMonitor: /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$37, [["render", _sfc_render$37], ["__scopeId", "data-v-39f2e9b8"]])
	},
	setup() {
		const { loading, makeRequest } = useApi();
		return {
			loading,
			makeRequest
		};
	},
	data() {
		return {
			showMetrics: true,
			revenuePeriod: "7d",
			growthPeriod: "30d",
			metrics: {},
			revenueData: [],
			clientGrowthData: [],
			systemStats: [],
			systemStatusInterval: 3e4,
			systemStatusTimer: null,
			packageSales: [],
			paymentMethods: [],
			packageColors: [
				"#3B82F6",
				"#10B981",
				"#F59E0B",
				"#EF4444",
				"#8B5CF6",
				"#EC4899",
				"#06B6D4",
				"#F97316"
			],
			paymentColors: [
				"#06B6D4",
				"#10B981",
				"#F59E0B",
				"#8B5CF6"
			],
			locationPerformance: [],
			recentActivity: [],
			voucherStatus: {},
			conversionFunnel: {},
			deviceBreakdown: [],
			rewardTiers: [],
			refundMetrics: {},
			dateRange: {
				start: "",
				end: "",
				compare: false
			},
			selectedLocations: [],
			selectedPackages: [],
			locationOptions: [],
			packageOptions: [],
			revenueChartOptions: {
				chart: {
					type: "area",
					toolbar: { show: false },
					zoom: { enabled: false }
				},
				colors: ["#10B981"],
				dataLabels: { enabled: false },
				stroke: {
					curve: "smooth",
					width: 2
				},
				fill: {
					type: "gradient",
					gradient: {
						opacityFrom: .4,
						opacityTo: .1
					}
				},
				xaxis: {
					type: "datetime",
					labels: { style: {
						colors: "#94a3b8",
						fontSize: "11px"
					} }
				},
				yaxis: { labels: {
					style: {
						colors: "#94a3b8",
						fontSize: "11px"
					},
					formatter: (v) => `${this.formatNumber(v)}`
				} },
				grid: {
					borderColor: "#e2e8f0",
					strokeDashArray: 3
				},
				tooltip: { theme: "dark" }
			},
			revenueChartSeries: [{
				name: "Revenue",
				data: []
			}],
			growthChartOptions: {
				chart: {
					type: "bar",
					toolbar: { show: false }
				},
				colors: ["#8B5CF6"],
				plotOptions: { bar: {
					borderRadius: 4,
					columnWidth: "60%"
				} },
				dataLabels: { enabled: false },
				xaxis: {
					type: "datetime",
					labels: { style: {
						colors: "#94a3b8",
						fontSize: "11px"
					} }
				},
				yaxis: { labels: { style: {
					colors: "#94a3b8",
					fontSize: "11px"
				} } },
				grid: {
					borderColor: "#e2e8f0",
					strokeDashArray: 3
				},
				tooltip: { theme: "dark" }
			},
			growthChartSeries: [{
				name: "Signups",
				data: []
			}],
			packageChartOptions: {
				chart: { type: "pie" },
				colors: [
					"#3B82F6",
					"#10B981",
					"#F59E0B",
					"#EF4444",
					"#8B5CF6",
					"#EC4899",
					"#06B6D4",
					"#F97316"
				],
				labels: [],
				legend: {
					position: "right",
					fontSize: "12px",
					offsetY: 0,
					height: 320,
					markers: {
						width: 12,
						height: 12,
						radius: 2
					},
					itemMargin: {
						horizontal: 5,
						vertical: 5
					}
				},
				dataLabels: {
					enabled: true,
					style: {
						fontSize: "14px",
						fontWeight: "bold"
					},
					dropShadow: { enabled: false }
				},
				stroke: {
					width: 2,
					colors: ["#fff"]
				},
				tooltip: { y: { formatter: (val) => `${val} sales` } },
				responsive: [{
					breakpoint: 480,
					options: { legend: { position: "bottom" } }
				}]
			},
			packageChartSeries: [],
			paymentChartOptions: {
				chart: { type: "pie" },
				colors: [
					"#06B6D4",
					"#10B981",
					"#F59E0B",
					"#8B5CF6"
				],
				labels: [],
				legend: {
					position: "bottom",
					fontSize: "11px"
				},
				dataLabels: {
					enabled: true,
					style: {
						fontSize: "12px",
						fontWeight: "bold"
					},
					dropShadow: {
						enabled: true,
						blur: 2,
						opacity: .5
					}
				},
				plotOptions: { pie: { expandOnClick: true } },
				stroke: {
					width: 2,
					colors: ["#fff"]
				},
				tooltip: { y: { formatter: (val) => `${val} transactions` } }
			},
			paymentChartSeries: []
		};
	},
	computed: {
		exportData() {
			return {
				metrics: this.metrics,
				revenueData: this.revenueData,
				clientGrowthData: this.clientGrowthData,
				packageSales: this.packageSales,
				locationPerformance: this.locationPerformance
			};
		},
		exportFilename() {
			return `dashboard-report-${(/* @__PURE__ */ new Date()).toISOString().split("T")[0]}`;
		}
	},
	async mounted() {
		await this.fetchFilterOptions();
		await this.fetchAllData();
		this.updateSystemStatusInterval();
	},
	beforeUnmount() {
		if (this.systemStatusTimer) clearInterval(this.systemStatusTimer);
	},
	methods: {
		async fetchFilterOptions() {
			try {
				this.locationOptions = (await this.makeRequest("get", "suapi/locations/")).results?.map((l) => ({
					value: l.id,
					label: l.name
				})) || [];
				this.packageOptions = (await this.makeRequest("get", "suapi/packages/")).results?.map((p) => ({
					value: p.id,
					label: p.name
				})) || [];
			} catch (error) {
				console.error("Error fetching filter options:", error);
			}
		},
		handleDateChange(range) {
			this.dateRange = range;
			this.fetchAllData();
		},
		handleLocationFilter(locations) {
			this.selectedLocations = locations;
			this.fetchAllData();
		},
		handlePackageFilter(packages) {
			this.selectedPackages = packages;
			this.fetchAllData();
		},
		async fetchAllData() {
			await Promise.all([
				this.fetchDashboardMetrics(),
				this.fetchRevenueAnalytics(),
				this.fetchClientGrowth(),
				this.fetchSystemStatus(),
				this.fetchPackageSales(),
				this.fetchPaymentMethods(),
				this.fetchLocationPerformance(),
				this.fetchRecentActivity(),
				this.fetchVoucherStatus(),
				this.fetchConversionFunnel(),
				this.fetchDeviceBreakdown(),
				this.fetchRewardTiers(),
				this.fetchRefundMetrics()
			]);
		},
		async fetchDashboardMetrics() {
			try {
				let url = "suapi/dashboard-metrics/";
				const params = new URLSearchParams();
				if (this.dateRange.start) params.append("start_date", this.dateRange.start);
				if (this.dateRange.end) params.append("end_date", this.dateRange.end);
				if (this.selectedLocations.length) params.append("locations", this.selectedLocations.join(","));
				if (this.selectedPackages.length) params.append("packages", this.selectedPackages.join(","));
				if (params.toString()) url += `?${params.toString()}`;
				this.metrics = await this.makeRequest("get", url);
			} catch (error) {
				console.error("Error fetching metrics:", error);
			}
		},
		async fetchRevenueAnalytics() {
			try {
				let url = `suapi/dashboard-metrics/revenue-analytics/?period=${this.revenuePeriod}`;
				const params = new URLSearchParams({ period: this.revenuePeriod });
				if (this.dateRange.start) params.append("start_date", this.dateRange.start);
				if (this.dateRange.end) params.append("end_date", this.dateRange.end);
				if (this.selectedLocations.length) params.append("locations", this.selectedLocations.join(","));
				if (this.selectedPackages.length) params.append("packages", this.selectedPackages.join(","));
				url = `suapi/dashboard-metrics/revenue-analytics/?${params.toString()}`;
				this.revenueData = (await this.makeRequest("get", url)).data;
				this.revenueChartSeries = [{
					name: "Revenue",
					data: this.revenueData.map((item) => ({
						x: new Date(item.date).getTime(),
						y: item.revenue
					}))
				}];
			} catch (error) {
				console.error("Error fetching revenue:", error);
			}
		},
		async fetchClientGrowth() {
			try {
				let url = `suapi/dashboard-metrics/client-growth/?period=${this.growthPeriod}`;
				const params = new URLSearchParams({ period: this.growthPeriod });
				if (this.dateRange.start) params.append("start_date", this.dateRange.start);
				if (this.dateRange.end) params.append("end_date", this.dateRange.end);
				if (this.selectedLocations.length) params.append("locations", this.selectedLocations.join(","));
				url = `suapi/dashboard-metrics/client-growth/?${params.toString()}`;
				this.clientGrowthData = (await this.makeRequest("get", url)).data;
				this.growthChartSeries = [{
					name: "Signups",
					data: this.clientGrowthData.map((item) => ({
						x: new Date(item.date).getTime(),
						y: item.signups
					}))
				}];
			} catch (error) {
				console.error("Error fetching growth:", error);
			}
		},
		async fetchSystemStatus() {
			try {
				const data = await this.makeRequest("get", "suapi/system-status/");
				this.systemStats = [
					{
						name: "Database",
						value: data.database_response,
						statusColor: data.database_status === "healthy" ? "bg-emerald-500" : data.database_status === "warning" ? "bg-amber-500" : "bg-rose-500"
					},
					{
						name: "Internet",
						value: data.internet_response,
						statusColor: data.internet_status === "healthy" ? "bg-emerald-500" : data.internet_status === "warning" ? "bg-amber-500" : "bg-rose-500"
					},
					{
						name: "Cache",
						value: data.cache_response,
						statusColor: data.cache_status === "healthy" ? "bg-emerald-500" : data.cache_status === "warning" ? "bg-amber-500" : "bg-rose-500"
					},
					{
						name: "Disk",
						value: data.disk_usage,
						statusColor: data.disk_status === "healthy" ? "bg-emerald-500" : data.disk_status === "warning" ? "bg-amber-500" : "bg-rose-500"
					}
				];
			} catch (error) {
				console.error("Error fetching system status:", error);
			}
		},
		updateSystemStatusInterval() {
			if (this.systemStatusTimer) clearInterval(this.systemStatusTimer);
			this.systemStatusTimer = setInterval(() => {
				this.fetchSystemStatus();
			}, parseInt(this.systemStatusInterval));
		},
		async fetchPackageSales() {
			try {
				let url = "suapi/dashboard-metrics/package-sales/";
				const params = new URLSearchParams();
				if (this.dateRange.start) params.append("start_date", this.dateRange.start);
				if (this.dateRange.end) params.append("end_date", this.dateRange.end);
				if (this.selectedLocations.length) params.append("locations", this.selectedLocations.join(","));
				if (this.selectedPackages.length) params.append("packages", this.selectedPackages.join(","));
				if (params.toString()) url += `?${params.toString()}`;
				this.packageSales = (await this.makeRequest("get", url)).data;
				this.packageChartOptions.labels = this.packageSales.map((p) => p.package__name || "Unknown");
				this.packageChartSeries = this.packageSales.map((p) => p.count);
			} catch (error) {
				console.error("Error fetching package sales:", error);
			}
		},
		async fetchPaymentMethods() {
			try {
				this.paymentMethods = (await this.makeRequest("get", "suapi/dashboard-metrics/payment-methods/")).data;
				this.paymentChartOptions.labels = this.paymentMethods.map((p) => p.payment_method || "Unknown");
				this.paymentChartSeries = this.paymentMethods.map((p) => p.count);
			} catch (error) {
				console.error("Error fetching payment methods:", error);
			}
		},
		async fetchLocationPerformance() {
			try {
				let url = "suapi/dashboard-metrics/location-performance/";
				const params = new URLSearchParams();
				if (this.dateRange.start) params.append("start_date", this.dateRange.start);
				if (this.dateRange.end) params.append("end_date", this.dateRange.end);
				if (this.selectedLocations.length) params.append("locations", this.selectedLocations.join(","));
				if (this.selectedPackages.length) params.append("packages", this.selectedPackages.join(","));
				if (params.toString()) url += `?${params.toString()}`;
				this.locationPerformance = (await this.makeRequest("get", url)).data;
			} catch (error) {
				console.error("Error fetching location performance:", error);
			}
		},
		async fetchRecentActivity() {
			try {
				this.recentActivity = (await this.makeRequest("get", "suapi/dashboard-metrics/recent-activity/")).data;
			} catch (error) {
				console.error("Error fetching recent activity:", error);
			}
		},
		async fetchVoucherStatus() {
			try {
				this.voucherStatus = await this.makeRequest("get", "suapi/dashboard-metrics/voucher-status/");
			} catch (error) {
				console.error("Error fetching voucher status:", error);
			}
		},
		async fetchConversionFunnel() {
			try {
				this.conversionFunnel = await this.makeRequest("get", "suapi/dashboard-metrics/conversion-funnel/");
			} catch (error) {
				console.error("Error fetching conversion funnel:", error);
			}
		},
		async fetchDeviceBreakdown() {
			try {
				this.deviceBreakdown = (await this.makeRequest("get", "suapi/dashboard-metrics/device-breakdown/")).data;
			} catch (error) {
				console.error("Error fetching device breakdown:", error);
			}
		},
		async fetchRewardTiers() {
			try {
				this.rewardTiers = (await this.makeRequest("get", "suapi/dashboard-metrics/reward-tiers/")).data;
			} catch (error) {
				console.error("Error fetching reward tiers:", error);
			}
		},
		async fetchRefundMetrics() {
			try {
				this.refundMetrics = await this.makeRequest("get", "suapi/dashboard-metrics/refund-metrics/");
			} catch (error) {
				console.error("Error fetching refund metrics:", error);
			}
		},
		refreshData() {
			this.fetchAllData();
		},
		formatNumber(num) {
			return new Intl.NumberFormat().format(num);
		},
		formatTime(isoString) {
			const date = new Date(isoString);
			const now = /* @__PURE__ */ new Date();
			const diff = Math.floor((now - date) / 1e3);
			if (diff < 60) return "Just now";
			if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
			if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
			return `${Math.floor(diff / 86400)}d ago`;
		},
		toggleMetrics() {
			this.showMetrics = !this.showMetrics;
		}
	}
};
var _hoisted_1$36 = { class: "space-y-6 animate-fade-in" };
var _hoisted_2$36 = { class: "flex items-center justify-between" };
var _hoisted_3$36 = { class: "flex items-center gap-3" };
var _hoisted_4$36 = { class: "relative my-8" };
var _hoisted_5$36 = { class: "relative flex justify-center" };
var _hoisted_6$36 = { class: "flex items-center gap-2" };
var _hoisted_7$36 = { class: "space-y-6" };
var _hoisted_8$35 = { class: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-slide-up" };
var _hoisted_9$33 = {
	class: "grid grid-cols-1 lg:grid-cols-2 gap-4 animate-slide-up",
	style: { "animation-delay": "0.1s" }
};
var _hoisted_10$31 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 transition-colors duration-300" };
var _hoisted_11$30 = { class: "flex items-center justify-between mb-4" };
var _hoisted_12$30 = {
	key: 0,
	class: "h-64"
};
var _hoisted_13$30 = {
	key: 1,
	class: "h-64 flex items-center justify-center text-slate-400 dark:text-slate-500 text-sm"
};
var _hoisted_14$30 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 transition-colors duration-300" };
var _hoisted_15$30 = { class: "flex items-center justify-between mb-4" };
var _hoisted_16$30 = {
	key: 0,
	class: "h-64"
};
var _hoisted_17$30 = {
	key: 1,
	class: "h-64 flex items-center justify-center text-slate-400 dark:text-slate-500 text-sm"
};
var _hoisted_18$30 = {
	class: "grid grid-cols-1 lg:grid-cols-2 gap-4 animate-slide-up",
	style: { "animation-delay": "0.15s" }
};
var _hoisted_19$26 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5" };
var _hoisted_20$26 = {
	key: 0,
	class: "h-96"
};
var _hoisted_21$25 = {
	key: 1,
	class: "h-64 flex items-center justify-center text-slate-400 text-sm"
};
var _hoisted_22$25 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5" };
var _hoisted_23$24 = {
	key: 0,
	class: "h-64"
};
var _hoisted_24$23 = {
	key: 1,
	class: "h-64 flex items-center justify-center text-slate-400 text-sm"
};
var _hoisted_25$23 = {
	class: "grid grid-cols-1 lg:grid-cols-2 gap-4 animate-slide-up",
	style: { "animation-delay": "0.2s" }
};
var _hoisted_26$23 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5" };
var _hoisted_27$22 = { class: "grid grid-cols-3 gap-3" };
var _hoisted_28$22 = { class: "bg-emerald-50 dark:bg-emerald-500/10 rounded-lg p-4 text-center" };
var _hoisted_29$22 = { class: "text-2xl font-bold text-emerald-600 dark:text-emerald-400" };
var _hoisted_30$21 = { class: "bg-amber-50 dark:bg-amber-500/10 rounded-lg p-4 text-center" };
var _hoisted_31$20 = { class: "text-2xl font-bold text-amber-600 dark:text-amber-400" };
var _hoisted_32$19 = { class: "bg-slate-50 dark:bg-slate-700 rounded-lg p-4 text-center" };
var _hoisted_33$19 = { class: "text-2xl font-bold text-slate-600 dark:text-slate-400" };
var _hoisted_34$19 = { class: "mt-4 pt-4 border-t border-slate-200 dark:border-slate-700" };
var _hoisted_35$18 = { class: "flex justify-between text-sm" };
var _hoisted_36$18 = { class: "font-semibold text-slate-900 dark:text-white" };
var _hoisted_37$18 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5" };
var _hoisted_38$18 = { class: "space-y-3" };
var _hoisted_39$18 = { class: "relative" };
var _hoisted_40$18 = { class: "flex justify-between text-sm mb-1" };
var _hoisted_41$17 = { class: "font-semibold text-slate-900 dark:text-white" };
var _hoisted_42$15 = { class: "relative" };
var _hoisted_43$14 = { class: "flex justify-between text-sm mb-1" };
var _hoisted_44$14 = { class: "font-semibold text-slate-900 dark:text-white" };
var _hoisted_45$11 = { class: "h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden" };
var _hoisted_46$11 = { class: "relative" };
var _hoisted_47$10 = { class: "flex justify-between text-sm mb-1" };
var _hoisted_48$7 = { class: "font-semibold text-slate-900 dark:text-white" };
var _hoisted_49$7 = { class: "h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden" };
var _hoisted_50$7 = { class: "mt-4 pt-4 border-t border-slate-200 dark:border-slate-700" };
var _hoisted_51$7 = { class: "flex justify-between text-sm" };
var _hoisted_52$6 = { class: "font-semibold text-emerald-600 dark:text-emerald-400" };
var _hoisted_53$6 = {
	class: "grid grid-cols-1 lg:grid-cols-2 gap-4 animate-slide-up",
	style: { "animation-delay": "0.25s" }
};
var _hoisted_54$5 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5" };
var _hoisted_55$4 = { class: "space-y-2 max-h-64 overflow-y-auto" };
var _hoisted_56$3 = { class: "flex items-center gap-3" };
var _hoisted_57$3 = { class: "w-8 h-8 rounded-full bg-gradient-to-br from-rose-500 to-pink-500 flex items-center justify-center text-white text-xs font-bold" };
var _hoisted_58$3 = { class: "text-sm font-medium text-slate-900 dark:text-white" };
var _hoisted_59$3 = { class: "text-xs text-slate-500 dark:text-slate-400" };
var _hoisted_60$3 = { class: "text-sm font-semibold text-slate-900 dark:text-white" };
var _hoisted_61$1 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5" };
var _hoisted_62$1 = { class: "space-y-2 max-h-64 overflow-y-auto" };
var _hoisted_63$1 = {
	key: 0,
	class: "w-4 h-4 text-emerald-600 dark:text-emerald-400",
	fill: "currentColor",
	viewBox: "0 0 24 24"
};
var _hoisted_64$1 = {
	key: 1,
	class: "w-4 h-4 text-blue-600 dark:text-blue-400",
	fill: "currentColor",
	viewBox: "0 0 24 24"
};
var _hoisted_65 = { class: "flex-1 min-w-0" };
var _hoisted_66 = { class: "text-sm text-slate-900 dark:text-white" };
var _hoisted_67 = { class: "text-xs text-slate-500 dark:text-slate-400 mt-0.5" };
var _hoisted_68 = {
	class: "grid grid-cols-1 md:grid-cols-3 gap-4 animate-slide-up",
	style: { "animation-delay": "0.3s" }
};
var _hoisted_69 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5" };
var _hoisted_70 = {
	key: 0,
	class: "space-y-2"
};
var _hoisted_71 = { class: "text-sm text-slate-600 dark:text-slate-400" };
var _hoisted_72 = { class: "text-sm font-semibold text-slate-900 dark:text-white" };
var _hoisted_73 = {
	key: 1,
	class: "text-center text-slate-400 text-sm py-4"
};
var _hoisted_74 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5" };
var _hoisted_75 = {
	key: 0,
	class: "space-y-2"
};
var _hoisted_76 = { class: "text-sm text-slate-600 dark:text-slate-400" };
var _hoisted_77 = { class: "text-sm font-semibold text-slate-900 dark:text-white" };
var _hoisted_78 = {
	key: 1,
	class: "text-center text-slate-400 text-sm py-4"
};
var _hoisted_79 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5" };
var _hoisted_80 = { class: "space-y-3" };
var _hoisted_81 = { class: "flex justify-between items-center" };
var _hoisted_82 = { class: "text-sm font-semibold text-slate-900 dark:text-white" };
var _hoisted_83 = { class: "flex justify-between items-center" };
var _hoisted_84 = { class: "text-sm font-semibold text-slate-900 dark:text-white" };
var _hoisted_85 = { class: "flex justify-between items-center" };
var _hoisted_86 = { class: "text-sm font-semibold text-red-600 dark:text-red-400" };
var _hoisted_87 = {
	class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 transition-colors duration-300 animate-slide-up",
	style: { "animation-delay": "0.35s" }
};
var _hoisted_88 = { class: "flex items-center justify-between mb-4" };
var _hoisted_89 = { class: "grid grid-cols-2 md:grid-cols-4 gap-4" };
var _hoisted_90 = { class: "text-xs text-slate-500 dark:text-slate-400" };
var _hoisted_91 = { class: "text-sm font-medium text-slate-900 dark:text-white" };
function _sfc_render$36(_ctx, _cache, $props, $setup, $data, $options) {
	const _component_DateRangePicker = resolveComponent("DateRangePicker");
	const _component_MultiSelectFilter = resolveComponent("MultiSelectFilter");
	const _component_ExportButton = resolveComponent("ExportButton");
	const _component_RealTimeMonitor = resolveComponent("RealTimeMonitor");
	const _component_ModernMetricCard = resolveComponent("ModernMetricCard");
	const _component_apexchart = resolveComponent("apexchart");
	return openBlock(), createElementBlock("div", _hoisted_1$36, [
		createBaseVNode("div", _hoisted_2$36, [_cache[9] || (_cache[9] = createBaseVNode("div", null, [createBaseVNode("h1", { class: "text-2xl font-semibold text-slate-900 dark:text-white" }, "Dashboard"), createBaseVNode("p", { class: "text-sm text-slate-500 dark:text-slate-400 mt-1" }, "Welcome back, here's your overview")], -1)), createBaseVNode("div", _hoisted_3$36, [
			createVNode(_component_DateRangePicker, { onChange: $options.handleDateChange }, null, 8, ["onChange"]),
			createVNode(_component_MultiSelectFilter, {
				label: "Locations",
				options: $data.locationOptions,
				onChange: $options.handleLocationFilter
			}, null, 8, ["options", "onChange"]),
			createVNode(_component_MultiSelectFilter, {
				label: "Packages",
				options: $data.packageOptions,
				onChange: $options.handlePackageFilter
			}, null, 8, ["options", "onChange"]),
			createVNode(_component_ExportButton, {
				data: $options.exportData,
				filename: $options.exportFilename
			}, null, 8, ["data", "filename"]),
			createBaseVNode("button", {
				onClick: _cache[0] || (_cache[0] = (...args) => $options.refreshData && $options.refreshData(...args)),
				class: normalizeClass(["p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors", { "animate-spin": $setup.loading }])
			}, [..._cache[8] || (_cache[8] = [createBaseVNode("svg", {
				class: "w-5 h-5 text-slate-600 dark:text-slate-400",
				fill: "none",
				stroke: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
			})], -1)])], 2)
		])]),
		createVNode(_component_RealTimeMonitor),
		createBaseVNode("div", _hoisted_4$36, [_cache[12] || (_cache[12] = createBaseVNode("div", {
			class: "absolute inset-0 flex items-center",
			"aria-hidden": "true"
		}, [createBaseVNode("div", { class: "w-full border-t-2 border-slate-200 dark:border-slate-700" })], -1)), createBaseVNode("div", _hoisted_5$36, [createBaseVNode("button", {
			onClick: _cache[1] || (_cache[1] = (...args) => $options.toggleMetrics && $options.toggleMetrics(...args)),
			class: "bg-slate-50 dark:bg-slate-900 px-4 py-2 rounded-full border-2 border-slate-200 dark:border-slate-700 hover:border-blue-500 dark:hover:border-blue-400 transition-all group"
		}, [createBaseVNode("div", _hoisted_6$36, [_cache[11] || (_cache[11] = createBaseVNode("span", { class: "text-xs font-medium text-slate-600 dark:text-slate-400 group-hover:text-blue-600 dark:group-hover:text-blue-400" }, "Performance Metrics", -1)), (openBlock(), createElementBlock("svg", {
			class: normalizeClass(["w-4 h-4 text-slate-400 group-hover:text-blue-500 transition-transform duration-300", $data.showMetrics ? "rotate-180" : ""]),
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [..._cache[10] || (_cache[10] = [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M19 9l-7 7-7-7"
		}, null, -1)])], 2))])])])]),
		createVNode(Transition, {
			"enter-active-class": "transition-all duration-500 ease-out",
			"enter-from-class": "opacity-0 -translate-y-4 max-h-0",
			"enter-to-class": "opacity-100 translate-y-0 max-h-[5000px]",
			"leave-active-class": "transition-all duration-300 ease-in",
			"leave-from-class": "opacity-100 translate-y-0 max-h-[5000px]",
			"leave-to-class": "opacity-0 -translate-y-4 max-h-0"
		}, {
			default: withCtx(() => [withDirectives(createBaseVNode("div", _hoisted_7$36, [
				createBaseVNode("div", _hoisted_8$35, [
					createVNode(_component_ModernMetricCard, {
						title: "Total Clients",
						value: $data.metrics.totalClients || 0,
						trend: $data.metrics.clientsTrend || "stable",
						trendValue: $data.metrics.clientsTrendValue || "0%",
						color: "blue"
					}, {
						default: withCtx(() => [..._cache[13] || (_cache[13] = [createBaseVNode("svg", {
							class: "w-6 h-6",
							fill: "currentColor",
							viewBox: "0 0 24 24"
						}, [createBaseVNode("path", { d: "M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z" })], -1)])]),
						_: 1
					}, 8, [
						"value",
						"trend",
						"trendValue"
					]),
					createVNode(_component_ModernMetricCard, {
						title: "New (7d)",
						value: $data.metrics.newClients7d || 0,
						trend: $data.metrics.newClientsTrend || "stable",
						trendValue: $data.metrics.newClientsTrendValue || "0%",
						color: "emerald"
					}, {
						default: withCtx(() => [..._cache[14] || (_cache[14] = [createBaseVNode("svg", {
							class: "w-6 h-6",
							fill: "currentColor",
							viewBox: "0 0 24 24"
						}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" })], -1)])]),
						_: 1
					}, 8, [
						"value",
						"trend",
						"trendValue"
					]),
					createVNode(_component_ModernMetricCard, {
						title: "Active Vouchers",
						value: $data.metrics.activeUsers || 0,
						trend: $data.metrics.activeUsersTrend || "stable",
						trendValue: $data.metrics.activeUsersTrendValue || "0%",
						color: "green"
					}, {
						default: withCtx(() => [..._cache[15] || (_cache[15] = [createBaseVNode("svg", {
							class: "w-6 h-6",
							fill: "currentColor",
							viewBox: "0 0 24 24"
						}, [createBaseVNode("path", { d: "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" })], -1)])]),
						_: 1
					}, 8, [
						"value",
						"trend",
						"trendValue"
					]),
					createVNode(_component_ModernMetricCard, {
						title: "Revenue",
						value: `KSh ${$options.formatNumber($data.metrics.totalRevenue || 0)}`,
						trend: $data.metrics.revenueTrend || "stable",
						trendValue: $data.metrics.revenueTrendValue || "0%",
						color: "amber",
						formatted: false
					}, {
						default: withCtx(() => [..._cache[16] || (_cache[16] = [createBaseVNode("svg", {
							class: "w-6 h-6",
							fill: "currentColor",
							viewBox: "0 0 24 24"
						}, [createBaseVNode("path", { d: "M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z" })], -1)])]),
						_: 1
					}, 8, [
						"value",
						"trend",
						"trendValue"
					])
				]),
				createBaseVNode("div", _hoisted_9$33, [createBaseVNode("div", _hoisted_10$31, [createBaseVNode("div", _hoisted_11$30, [_cache[18] || (_cache[18] = createBaseVNode("div", { class: "flex items-center gap-2" }, [createBaseVNode("svg", {
					class: "w-5 h-5 text-emerald-500",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z" })]), createBaseVNode("h3", { class: "text-sm font-medium text-slate-900 dark:text-white" }, "Revenue Analytics")], -1)), withDirectives(createBaseVNode("select", {
					"onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => $data.revenuePeriod = $event),
					onChange: _cache[3] || (_cache[3] = (...args) => $options.fetchRevenueAnalytics && $options.fetchRevenueAnalytics(...args)),
					class: "text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg px-2 py-1 text-slate-900 dark:text-white"
				}, [..._cache[17] || (_cache[17] = [
					createBaseVNode("option", { value: "7d" }, "7 days", -1),
					createBaseVNode("option", { value: "14d" }, "14 days", -1),
					createBaseVNode("option", { value: "30d" }, "30 days", -1),
					createBaseVNode("option", { value: "90d" }, "90 days", -1),
					createBaseVNode("option", { value: "6m" }, "6 months", -1),
					createBaseVNode("option", { value: "1y" }, "1 year", -1)
				])], 544), [[vModelSelect, $data.revenuePeriod]])]), $data.revenueData.length > 0 ? (openBlock(), createElementBlock("div", _hoisted_12$30, [createVNode(_component_apexchart, {
					type: "area",
					height: "100%",
					options: $data.revenueChartOptions,
					series: $data.revenueChartSeries
				}, null, 8, ["options", "series"])])) : (openBlock(), createElementBlock("div", _hoisted_13$30, " Loading... "))]), createBaseVNode("div", _hoisted_14$30, [createBaseVNode("div", _hoisted_15$30, [_cache[20] || (_cache[20] = createBaseVNode("div", { class: "flex items-center gap-2" }, [createBaseVNode("svg", {
					class: "w-5 h-5 text-purple-500",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z" })]), createBaseVNode("h3", { class: "text-sm font-medium text-slate-900 dark:text-white" }, "Client Growth")], -1)), withDirectives(createBaseVNode("select", {
					"onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => $data.growthPeriod = $event),
					onChange: _cache[5] || (_cache[5] = (...args) => $options.fetchClientGrowth && $options.fetchClientGrowth(...args)),
					class: "text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg px-2 py-1 text-slate-900 dark:text-white"
				}, [..._cache[19] || (_cache[19] = [
					createBaseVNode("option", { value: "7d" }, "7 days", -1),
					createBaseVNode("option", { value: "14d" }, "14 days", -1),
					createBaseVNode("option", { value: "30d" }, "30 days", -1),
					createBaseVNode("option", { value: "90d" }, "90 days", -1),
					createBaseVNode("option", { value: "6m" }, "6 months", -1),
					createBaseVNode("option", { value: "1y" }, "1 year", -1)
				])], 544), [[vModelSelect, $data.growthPeriod]])]), $data.clientGrowthData.length > 0 ? (openBlock(), createElementBlock("div", _hoisted_16$30, [createVNode(_component_apexchart, {
					type: "bar",
					height: "100%",
					options: $data.growthChartOptions,
					series: $data.growthChartSeries
				}, null, 8, ["options", "series"])])) : (openBlock(), createElementBlock("div", _hoisted_17$30, " Loading... "))])]),
				createBaseVNode("div", _hoisted_18$30, [createBaseVNode("div", _hoisted_19$26, [_cache[21] || (_cache[21] = createBaseVNode("div", { class: "flex items-center gap-2 mb-4" }, [createBaseVNode("svg", {
					class: "w-5 h-5 text-blue-500",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M20 6h-2.18c.11-.31.18-.65.18-1 0-1.66-1.34-3-3-3-1.05 0-1.96.54-2.5 1.35l-.5.67-.5-.68C10.96 2.54 10.05 2 9 2 7.34 2 6 3.34 6 5c0 .35.07.69.18 1H4c-1.11 0-1.99.89-1.99 2L2 19c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2zm-5-2c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zM9 4c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm11 15H4v-2h16v2zm0-5H4V8h5.08L7 10.83 8.62 12 11 8.76l1-1.36 1 1.36L15.38 12 17 10.83 14.92 8H20v6z" })]), createBaseVNode("h3", { class: "text-sm font-medium text-slate-900 dark:text-white" }, "Package Sales")], -1)), $data.packageSales.length > 0 ? (openBlock(), createElementBlock("div", _hoisted_20$26, [createVNode(_component_apexchart, {
					type: "pie",
					height: "100%",
					options: $data.packageChartOptions,
					series: $data.packageChartSeries
				}, null, 8, ["options", "series"])])) : (openBlock(), createElementBlock("div", _hoisted_21$25, "Loading..."))]), createBaseVNode("div", _hoisted_22$25, [_cache[22] || (_cache[22] = createBaseVNode("div", { class: "flex items-center gap-2 mb-4" }, [createBaseVNode("svg", {
					class: "w-5 h-5 text-cyan-500",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M20 4H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z" })]), createBaseVNode("h3", { class: "text-sm font-medium text-slate-900 dark:text-white" }, "Payment Methods")], -1)), $data.paymentMethods.length > 0 ? (openBlock(), createElementBlock("div", _hoisted_23$24, [createVNode(_component_apexchart, {
					type: "pie",
					height: "100%",
					options: $data.paymentChartOptions,
					series: $data.paymentChartSeries
				}, null, 8, ["options", "series"])])) : (openBlock(), createElementBlock("div", _hoisted_24$23, "Loading..."))])]),
				createBaseVNode("div", _hoisted_25$23, [createBaseVNode("div", _hoisted_26$23, [
					_cache[27] || (_cache[27] = createBaseVNode("div", { class: "flex items-center gap-2 mb-4" }, [createBaseVNode("svg", {
						class: "w-5 h-5 text-orange-500",
						fill: "currentColor",
						viewBox: "0 0 24 24"
					}, [createBaseVNode("path", { d: "M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7C4.67 7 4 6.33 4 5.5S4.67 4 5.5 4 7 4.67 7 5.5 6.33 7 5.5 7z" })]), createBaseVNode("h3", { class: "text-sm font-medium text-slate-900 dark:text-white" }, "Voucher Status")], -1)),
					createBaseVNode("div", _hoisted_27$22, [
						createBaseVNode("div", _hoisted_28$22, [createBaseVNode("p", _hoisted_29$22, toDisplayString($data.voucherStatus.active || 0), 1), _cache[23] || (_cache[23] = createBaseVNode("p", { class: "text-xs text-slate-600 dark:text-slate-400 mt-1" }, "Active", -1))]),
						createBaseVNode("div", _hoisted_30$21, [createBaseVNode("p", _hoisted_31$20, toDisplayString($data.voucherStatus.pending || 0), 1), _cache[24] || (_cache[24] = createBaseVNode("p", { class: "text-xs text-slate-600 dark:text-slate-400 mt-1" }, "Pending", -1))]),
						createBaseVNode("div", _hoisted_32$19, [createBaseVNode("p", _hoisted_33$19, toDisplayString($data.voucherStatus.expired || 0), 1), _cache[25] || (_cache[25] = createBaseVNode("p", { class: "text-xs text-slate-600 dark:text-slate-400 mt-1" }, "Expired", -1))])
					]),
					createBaseVNode("div", _hoisted_34$19, [createBaseVNode("div", _hoisted_35$18, [_cache[26] || (_cache[26] = createBaseVNode("span", { class: "text-slate-600 dark:text-slate-400" }, "Total Vouchers", -1)), createBaseVNode("span", _hoisted_36$18, toDisplayString($data.voucherStatus.total || 0), 1)])])
				]), createBaseVNode("div", _hoisted_37$18, [_cache[33] || (_cache[33] = createBaseVNode("div", { class: "flex items-center gap-2 mb-4" }, [createBaseVNode("svg", {
					class: "w-5 h-5 text-indigo-500",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z" })]), createBaseVNode("h3", { class: "text-sm font-medium text-slate-900 dark:text-white" }, "Conversion Funnel")], -1)), createBaseVNode("div", _hoisted_38$18, [
					createBaseVNode("div", _hoisted_39$18, [createBaseVNode("div", _hoisted_40$18, [_cache[28] || (_cache[28] = createBaseVNode("span", { class: "text-slate-600 dark:text-slate-400" }, "Signups", -1)), createBaseVNode("span", _hoisted_41$17, toDisplayString($data.conversionFunnel.signups || 0), 1)]), _cache[29] || (_cache[29] = createBaseVNode("div", { class: "h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden" }, [createBaseVNode("div", {
						class: "h-full bg-blue-500",
						style: { "width": "100%" }
					})], -1))]),
					createBaseVNode("div", _hoisted_42$15, [createBaseVNode("div", _hoisted_43$14, [_cache[30] || (_cache[30] = createBaseVNode("span", { class: "text-slate-600 dark:text-slate-400" }, "Purchased", -1)), createBaseVNode("span", _hoisted_44$14, toDisplayString($data.conversionFunnel.purchased || 0), 1)]), createBaseVNode("div", _hoisted_45$11, [createBaseVNode("div", {
						class: "h-full bg-purple-500",
						style: normalizeStyle(`width: ${$data.conversionFunnel.purchased / $data.conversionFunnel.signups * 100 || 0}%`)
					}, null, 4)])]),
					createBaseVNode("div", _hoisted_46$11, [createBaseVNode("div", _hoisted_47$10, [_cache[31] || (_cache[31] = createBaseVNode("span", { class: "text-slate-600 dark:text-slate-400" }, "Active", -1)), createBaseVNode("span", _hoisted_48$7, toDisplayString($data.conversionFunnel.active || 0), 1)]), createBaseVNode("div", _hoisted_49$7, [createBaseVNode("div", {
						class: "h-full bg-emerald-500",
						style: normalizeStyle(`width: ${$data.conversionFunnel.active / $data.conversionFunnel.signups * 100 || 0}%`)
					}, null, 4)])]),
					createBaseVNode("div", _hoisted_50$7, [createBaseVNode("div", _hoisted_51$7, [_cache[32] || (_cache[32] = createBaseVNode("span", { class: "text-slate-600 dark:text-slate-400" }, "Conversion Rate", -1)), createBaseVNode("span", _hoisted_52$6, toDisplayString($data.conversionFunnel.conversion_rate || 0) + "%", 1)])])
				])])]),
				createBaseVNode("div", _hoisted_53$6, [createBaseVNode("div", _hoisted_54$5, [_cache[34] || (_cache[34] = createBaseVNode("div", { class: "flex items-center gap-2 mb-4" }, [createBaseVNode("svg", {
					class: "w-5 h-5 text-rose-500",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" })]), createBaseVNode("h3", { class: "text-sm font-medium text-slate-900 dark:text-white" }, "Top Locations")], -1)), createBaseVNode("div", _hoisted_55$4, [(openBlock(true), createElementBlock(Fragment, null, renderList($data.locationPerformance, (loc, idx) => {
					return openBlock(), createElementBlock("div", {
						key: idx,
						class: "flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg"
					}, [createBaseVNode("div", _hoisted_56$3, [createBaseVNode("div", _hoisted_57$3, toDisplayString(idx + 1), 1), createBaseVNode("div", null, [createBaseVNode("p", _hoisted_58$3, toDisplayString(loc.location__name || "Unknown"), 1), createBaseVNode("p", _hoisted_59$3, toDisplayString(loc.sales) + " sales", 1)])]), createBaseVNode("p", _hoisted_60$3, "KSh " + toDisplayString($options.formatNumber(loc.revenue || 0)), 1)]);
				}), 128))])]), createBaseVNode("div", _hoisted_61$1, [_cache[37] || (_cache[37] = createBaseVNode("div", { class: "flex items-center gap-2 mb-4" }, [createBaseVNode("svg", {
					class: "w-5 h-5 text-amber-500",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z" })]), createBaseVNode("h3", { class: "text-sm font-medium text-slate-900 dark:text-white" }, "Recent Activity")], -1)), createBaseVNode("div", _hoisted_62$1, [(openBlock(true), createElementBlock(Fragment, null, renderList($data.recentActivity, (activity) => {
					return openBlock(), createElementBlock("div", {
						key: activity.time,
						class: "flex items-start gap-3 p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg"
					}, [createBaseVNode("div", { class: normalizeClass(["w-8 h-8 rounded-full flex items-center justify-center", activity.type === "payment" ? "bg-emerald-100 dark:bg-emerald-500/20" : "bg-blue-100 dark:bg-blue-500/20"]) }, [activity.type === "payment" ? (openBlock(), createElementBlock("svg", _hoisted_63$1, [..._cache[35] || (_cache[35] = [createBaseVNode("path", { d: "M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z" }, null, -1)])])) : (openBlock(), createElementBlock("svg", _hoisted_64$1, [..._cache[36] || (_cache[36] = [createBaseVNode("path", { d: "M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" }, null, -1)])]))], 2), createBaseVNode("div", _hoisted_65, [createBaseVNode("p", _hoisted_66, toDisplayString(activity.description), 1), createBaseVNode("p", _hoisted_67, toDisplayString(activity.user) + " • " + toDisplayString($options.formatTime(activity.time)), 1)])]);
				}), 128))])])]),
				createBaseVNode("div", _hoisted_68, [
					createBaseVNode("div", _hoisted_69, [_cache[38] || (_cache[38] = createBaseVNode("div", { class: "flex items-center gap-2 mb-3" }, [createBaseVNode("svg", {
						class: "w-5 h-5 text-teal-500",
						fill: "currentColor",
						viewBox: "0 0 24 24"
					}, [createBaseVNode("path", { d: "M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z" })]), createBaseVNode("h3", { class: "text-sm font-medium text-slate-900 dark:text-white" }, "Device Breakdown")], -1)), $data.deviceBreakdown.length > 0 ? (openBlock(), createElementBlock("div", _hoisted_70, [(openBlock(true), createElementBlock(Fragment, null, renderList($data.deviceBreakdown, (device) => {
						return openBlock(), createElementBlock("div", {
							key: device.device_type,
							class: "flex justify-between items-center"
						}, [createBaseVNode("span", _hoisted_71, toDisplayString(device.device_type || "Unknown"), 1), createBaseVNode("span", _hoisted_72, toDisplayString(device.count), 1)]);
					}), 128))])) : (openBlock(), createElementBlock("div", _hoisted_73, "No data"))]),
					createBaseVNode("div", _hoisted_74, [_cache[39] || (_cache[39] = createBaseVNode("div", { class: "flex items-center gap-2 mb-3" }, [createBaseVNode("svg", {
						class: "w-5 h-5 text-yellow-500",
						fill: "currentColor",
						viewBox: "0 0 24 24"
					}, [createBaseVNode("path", { d: "M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" })]), createBaseVNode("h3", { class: "text-sm font-medium text-slate-900 dark:text-white" }, "Reward Tiers")], -1)), $data.rewardTiers.length > 0 ? (openBlock(), createElementBlock("div", _hoisted_75, [(openBlock(true), createElementBlock(Fragment, null, renderList($data.rewardTiers, (tier) => {
						return openBlock(), createElementBlock("div", {
							key: tier.reward_tier,
							class: "flex justify-between items-center"
						}, [createBaseVNode("span", _hoisted_76, toDisplayString(tier.reward_tier || "None"), 1), createBaseVNode("span", _hoisted_77, toDisplayString(tier.count), 1)]);
					}), 128))])) : (openBlock(), createElementBlock("div", _hoisted_78, "No data"))]),
					createBaseVNode("div", _hoisted_79, [_cache[43] || (_cache[43] = createBaseVNode("div", { class: "flex items-center gap-2 mb-3" }, [createBaseVNode("svg", {
						class: "w-5 h-5 text-red-500",
						fill: "currentColor",
						viewBox: "0 0 24 24"
					}, [createBaseVNode("path", { d: "M11 15h2v2h-2zm0-8h2v6h-2zm.99-5C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z" })]), createBaseVNode("h3", { class: "text-sm font-medium text-slate-900 dark:text-white" }, "Refund Metrics")], -1)), createBaseVNode("div", _hoisted_80, [
						createBaseVNode("div", _hoisted_81, [_cache[40] || (_cache[40] = createBaseVNode("span", { class: "text-sm text-slate-600 dark:text-slate-400" }, "Total Refunds", -1)), createBaseVNode("span", _hoisted_82, toDisplayString($data.refundMetrics.total_refunds || 0), 1)]),
						createBaseVNode("div", _hoisted_83, [_cache[41] || (_cache[41] = createBaseVNode("span", { class: "text-sm text-slate-600 dark:text-slate-400" }, "Amount", -1)), createBaseVNode("span", _hoisted_84, "KSh " + toDisplayString($options.formatNumber($data.refundMetrics.total_amount || 0)), 1)]),
						createBaseVNode("div", _hoisted_85, [_cache[42] || (_cache[42] = createBaseVNode("span", { class: "text-sm text-slate-600 dark:text-slate-400" }, "Refund Rate", -1)), createBaseVNode("span", _hoisted_86, toDisplayString($data.refundMetrics.refund_rate || 0) + "%", 1)])
					])])
				]),
				createBaseVNode("div", _hoisted_87, [createBaseVNode("div", _hoisted_88, [_cache[45] || (_cache[45] = createBaseVNode("div", { class: "flex items-center gap-2" }, [createBaseVNode("svg", {
					class: "w-5 h-5 text-green-500",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" })]), createBaseVNode("h3", { class: "text-sm font-medium text-slate-900 dark:text-white" }, "System Health")], -1)), withDirectives(createBaseVNode("select", {
					"onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => $data.systemStatusInterval = $event),
					onChange: _cache[7] || (_cache[7] = (...args) => $options.updateSystemStatusInterval && $options.updateSystemStatusInterval(...args)),
					class: "text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg px-2 py-1 text-slate-900 dark:text-white"
				}, [..._cache[44] || (_cache[44] = [
					createBaseVNode("option", { value: "5000" }, "5 seconds", -1),
					createBaseVNode("option", { value: "10000" }, "10 seconds", -1),
					createBaseVNode("option", { value: "30000" }, "30 seconds", -1),
					createBaseVNode("option", { value: "60000" }, "1 minute", -1),
					createBaseVNode("option", { value: "300000" }, "5 minutes", -1)
				])], 544), [[vModelSelect, $data.systemStatusInterval]])]), createBaseVNode("div", _hoisted_89, [(openBlock(true), createElementBlock(Fragment, null, renderList($data.systemStats, (stat) => {
					return openBlock(), createElementBlock("div", {
						key: stat.name,
						class: "flex items-center gap-3"
					}, [createBaseVNode("div", { class: normalizeClass(`w-2 h-2 rounded-full ${stat.statusColor}`) }, null, 2), createBaseVNode("div", null, [createBaseVNode("p", _hoisted_90, toDisplayString(stat.name), 1), createBaseVNode("p", _hoisted_91, toDisplayString(stat.value), 1)])]);
				}), 128))])])
			], 512), [[vShow, $data.showMetrics]])]),
			_: 1
		})
	]);
}
var Dashboard_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$36, [["render", _sfc_render$36], ["__scopeId", "data-v-5788c941"]]);
var _sfc_main$35 = {
	name: "FinancialAnalytics",
	data() {
		return { showGuide: false };
	},
	props: {
		metrics: {
			type: Object,
			default: () => ({
				mrr: 0,
				arr: 0,
				arpu: 0,
				ltv: 0,
				growth_rate: 0
			})
		},
		packages: {
			type: Array,
			default: () => []
		},
		loading: {
			type: Boolean,
			default: false
		}
	},
	methods: { formatNumber(num) {
		return new Intl.NumberFormat().format(num);
	} }
};
var _hoisted_1$35 = { class: "space-y-4" };
var _hoisted_2$35 = { class: "bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl border border-blue-200 dark:border-blue-800 p-4" };
var _hoisted_3$35 = { class: "mt-4 space-y-3 text-xs" };
var _hoisted_4$35 = { class: "grid grid-cols-1 md:grid-cols-4 gap-4" };
var _hoisted_5$35 = { class: "bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700" };
var _hoisted_6$35 = { class: "text-2xl font-bold text-slate-900 dark:text-white" };
var _hoisted_7$35 = { class: "text-xs text-emerald-600 dark:text-emerald-400 mt-1" };
var _hoisted_8$34 = { class: "bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700" };
var _hoisted_9$32 = { class: "text-2xl font-bold text-slate-900 dark:text-white" };
var _hoisted_10$30 = { class: "bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700" };
var _hoisted_11$29 = { class: "text-2xl font-bold text-slate-900 dark:text-white" };
var _hoisted_12$29 = { class: "bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700" };
var _hoisted_13$29 = { class: "text-2xl font-bold text-slate-900 dark:text-white" };
var _hoisted_14$29 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5" };
var _hoisted_15$29 = {
	key: 0,
	class: "text-center py-8 text-slate-400"
};
var _hoisted_16$29 = {
	key: 1,
	class: "overflow-x-auto"
};
var _hoisted_17$29 = { class: "w-full text-xs" };
var _hoisted_18$29 = { class: "p-2 font-medium text-slate-900 dark:text-white" };
var _hoisted_19$25 = { class: "p-2 text-center text-slate-900 dark:text-white" };
var _hoisted_20$25 = { class: "p-2 text-center text-slate-900 dark:text-white" };
var _hoisted_21$24 = { class: "p-2 text-center text-slate-900 dark:text-white" };
var _hoisted_22$24 = { class: "p-2 text-center" };
function _sfc_render$35(_ctx, _cache, $props, $setup, $data, $options) {
	return openBlock(), createElementBlock("div", _hoisted_1$35, [
		createBaseVNode("div", _hoisted_2$35, [createBaseVNode("button", {
			onClick: _cache[0] || (_cache[0] = ($event) => $data.showGuide = !$data.showGuide),
			class: "flex items-center justify-between w-full text-left"
		}, [_cache[2] || (_cache[2] = createBaseVNode("div", { class: "flex items-center gap-2" }, [createBaseVNode("svg", {
			class: "w-5 h-5 text-blue-600 dark:text-blue-400",
			fill: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z" })]), createBaseVNode("span", { class: "text-sm font-medium text-blue-900 dark:text-blue-100" }, "Financial Metrics Guide")], -1)), (openBlock(), createElementBlock("svg", {
			class: normalizeClass(["w-4 h-4 text-blue-600 dark:text-blue-400 transition-transform", $data.showGuide ? "rotate-180" : ""]),
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [..._cache[1] || (_cache[1] = [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M19 9l-7 7-7-7"
		}, null, -1)])], 2))]), withDirectives(createBaseVNode("div", _hoisted_3$35, [..._cache[3] || (_cache[3] = [createStaticVNode("<div class=\"grid grid-cols-1 md:grid-cols-2 gap-3\"><div class=\"bg-white dark:bg-slate-800 rounded-lg p-3 border border-blue-100 dark:border-blue-900\"><div class=\"flex items-center gap-2 mb-2\"><div class=\"w-2 h-2 rounded-full bg-blue-500\"></div><span class=\"font-semibold text-blue-900 dark:text-blue-100\">MRR (Monthly Recurring Revenue)</span></div><p class=\"text-slate-600 dark:text-slate-400 mb-2\">Total revenue from completed M-Pesa transactions in the current month.</p><div class=\"bg-slate-50 dark:bg-slate-900 rounded p-2 font-mono text-[10px] text-slate-700 dark:text-slate-300\"> Sum of TransactionQueue.price<br> WHERE method=&#39;mpesa&#39;<br> AND status IN [&#39;completed&#39;, &#39;processed&#39;]<br> AND created_at &gt;= current_month_start </div></div><div class=\"bg-white dark:bg-slate-800 rounded-lg p-3 border border-emerald-100 dark:border-emerald-900\"><div class=\"flex items-center gap-2 mb-2\"><div class=\"w-2 h-2 rounded-full bg-emerald-500\"></div><span class=\"font-semibold text-emerald-900 dark:text-emerald-100\">ARR (Annual Recurring Revenue)</span></div><p class=\"text-slate-600 dark:text-slate-400 mb-2\">Total revenue from completed M-Pesa transactions in the current year.</p><div class=\"bg-slate-50 dark:bg-slate-900 rounded p-2 font-mono text-[10px] text-slate-700 dark:text-slate-300\"> Sum of TransactionQueue.price<br> WHERE method=&#39;mpesa&#39;<br> AND status IN [&#39;completed&#39;, &#39;processed&#39;]<br> AND created_at &gt;= current_year_start </div></div><div class=\"bg-white dark:bg-slate-800 rounded-lg p-3 border border-purple-100 dark:border-purple-900\"><div class=\"flex items-center gap-2 mb-2\"><div class=\"w-2 h-2 rounded-full bg-purple-500\"></div><span class=\"font-semibold text-purple-900 dark:text-purple-100\">ARPU (Average Revenue Per User)</span></div><p class=\"text-slate-600 dark:text-slate-400 mb-2\">Average monthly revenue generated per active user.</p><div class=\"bg-slate-50 dark:bg-slate-900 rounded p-2 font-mono text-[10px] text-slate-700 dark:text-slate-300\"> ARPU = MRR / Active Users<br><br> Active Users = Count of users with<br> active vouchers (status=&#39;active&#39;<br> AND expires_at &gt; now) </div></div><div class=\"bg-white dark:bg-slate-800 rounded-lg p-3 border border-amber-100 dark:border-amber-900\"><div class=\"flex items-center gap-2 mb-2\"><div class=\"w-2 h-2 rounded-full bg-amber-500\"></div><span class=\"font-semibold text-amber-900 dark:text-amber-100\">LTV (Lifetime Value)</span></div><p class=\"text-slate-600 dark:text-slate-400 mb-2\">Estimated total revenue from a customer over their lifetime (12 months).</p><div class=\"bg-slate-50 dark:bg-slate-900 rounded p-2 font-mono text-[10px] text-slate-700 dark:text-slate-300\"> LTV = ARPU × 12 months<br><br> Represents expected revenue<br> from a customer over one year<br> based on current monthly average </div></div></div><div class=\"bg-white dark:bg-slate-800 rounded-lg p-3 border border-slate-200 dark:border-slate-700\"><div class=\"flex items-center gap-2 mb-2\"><svg class=\"w-4 h-4 text-slate-600 dark:text-slate-400\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z\"></path></svg><span class=\"font-semibold text-slate-900 dark:text-slate-100\">Growth Rate Calculation</span></div><p class=\"text-slate-600 dark:text-slate-400\">Growth rate compares current month MRR vs previous month MRR: <span class=\"font-mono bg-slate-100 dark:bg-slate-900 px-2 py-1 rounded\">((Current MRR - Previous MRR) / Previous MRR) × 100</span></p></div><div class=\"bg-amber-50 dark:bg-amber-900/20 rounded-lg p-3 border border-amber-200 dark:border-amber-800\"><div class=\"flex items-start gap-2\"><svg class=\"w-4 h-4 text-amber-600 dark:text-amber-400 mt-0.5\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z\"></path></svg><div><span class=\"font-semibold text-amber-900 dark:text-amber-100 text-xs\">Data Source:</span><p class=\"text-amber-800 dark:text-amber-200 text-xs mt-1\">All financial metrics are calculated from the <span class=\"font-mono bg-amber-100 dark:bg-amber-900 px-1 rounded\">TransactionQueue</span> table, filtering only completed and processed M-Pesa transactions to ensure accuracy and prevent duplicate counting.</p></div></div></div>", 3)])], 512), [[vShow, $data.showGuide]])]),
		createBaseVNode("div", _hoisted_4$35, [
			createBaseVNode("div", _hoisted_5$35, [
				_cache[4] || (_cache[4] = createBaseVNode("div", { class: "flex items-center gap-2 mb-2" }, [createBaseVNode("svg", {
					class: "w-5 h-5 text-blue-500",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1.41 16.09V20h-2.67v-1.93c-1.71-.36-3.16-1.46-3.27-3.4h1.96c.1 1.05.82 1.87 2.65 1.87 1.96 0 2.4-.98 2.4-1.59 0-.83-.44-1.61-2.67-2.14-2.48-.6-4.18-1.62-4.18-3.67 0-1.72 1.39-2.84 3.11-3.21V4h2.67v1.95c1.86.45 2.79 1.86 2.85 3.39H14.3c-.05-1.11-.64-1.87-2.22-1.87-1.5 0-2.4.68-2.4 1.64 0 .84.65 1.39 2.67 1.91s4.18 1.39 4.18 3.91c-.01 1.83-1.38 2.83-3.12 3.16z" })]), createBaseVNode("span", { class: "text-xs text-slate-600 dark:text-slate-400" }, "MRR")], -1)),
				createBaseVNode("p", _hoisted_6$35, "KSh " + toDisplayString($options.formatNumber($props.metrics.mrr)), 1),
				createBaseVNode("p", _hoisted_7$35, "+" + toDisplayString($props.metrics.growth_rate) + "% growth", 1)
			]),
			createBaseVNode("div", _hoisted_8$34, [
				_cache[5] || (_cache[5] = createBaseVNode("div", { class: "flex items-center gap-2 mb-2" }, [createBaseVNode("svg", {
					class: "w-5 h-5 text-emerald-500",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z" })]), createBaseVNode("span", { class: "text-xs text-slate-600 dark:text-slate-400" }, "ARR")], -1)),
				createBaseVNode("p", _hoisted_9$32, "KSh " + toDisplayString($options.formatNumber($props.metrics.arr)), 1),
				_cache[6] || (_cache[6] = createBaseVNode("p", { class: "text-xs text-slate-500 dark:text-slate-400 mt-1" }, "Annual recurring", -1))
			]),
			createBaseVNode("div", _hoisted_10$30, [
				_cache[7] || (_cache[7] = createBaseVNode("div", { class: "flex items-center gap-2 mb-2" }, [createBaseVNode("svg", {
					class: "w-5 h-5 text-purple-500",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" })]), createBaseVNode("span", { class: "text-xs text-slate-600 dark:text-slate-400" }, "ARPU")], -1)),
				createBaseVNode("p", _hoisted_11$29, "KSh " + toDisplayString($options.formatNumber($props.metrics.arpu)), 1),
				_cache[8] || (_cache[8] = createBaseVNode("p", { class: "text-xs text-slate-500 dark:text-slate-400 mt-1" }, "Per user/month", -1))
			]),
			createBaseVNode("div", _hoisted_12$29, [
				_cache[9] || (_cache[9] = createBaseVNode("div", { class: "flex items-center gap-2 mb-2" }, [createBaseVNode("svg", {
					class: "w-5 h-5 text-amber-500",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" })]), createBaseVNode("span", { class: "text-xs text-slate-600 dark:text-slate-400" }, "LTV")], -1)),
				createBaseVNode("p", _hoisted_13$29, "KSh " + toDisplayString($options.formatNumber($props.metrics.ltv)), 1),
				_cache[10] || (_cache[10] = createBaseVNode("p", { class: "text-xs text-slate-500 dark:text-slate-400 mt-1" }, "Lifetime value", -1))
			])
		]),
		createBaseVNode("div", _hoisted_14$29, [_cache[12] || (_cache[12] = createBaseVNode("div", { class: "flex items-center gap-2 mb-4" }, [createBaseVNode("svg", {
			class: "w-5 h-5 text-cyan-500",
			fill: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", { d: "M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z" })]), createBaseVNode("h3", { class: "text-sm font-medium text-slate-900 dark:text-white" }, "Package Performance & Margins")], -1)), $props.loading ? (openBlock(), createElementBlock("div", _hoisted_15$29, "Loading...")) : (openBlock(), createElementBlock("div", _hoisted_16$29, [createBaseVNode("table", _hoisted_17$29, [_cache[11] || (_cache[11] = createBaseVNode("thead", { class: "border-b border-slate-200 dark:border-slate-700" }, [createBaseVNode("tr", null, [
			createBaseVNode("th", { class: "text-left p-2 text-slate-600 dark:text-slate-400" }, "Package"),
			createBaseVNode("th", { class: "text-center p-2 text-slate-600 dark:text-slate-400" }, "Sales"),
			createBaseVNode("th", { class: "text-center p-2 text-slate-600 dark:text-slate-400" }, "Revenue"),
			createBaseVNode("th", { class: "text-center p-2 text-slate-600 dark:text-slate-400" }, "Profit"),
			createBaseVNode("th", { class: "text-center p-2 text-slate-600 dark:text-slate-400" }, "Margin")
		])], -1)), createBaseVNode("tbody", null, [(openBlock(true), createElementBlock(Fragment, null, renderList($props.packages, (pkg) => {
			return openBlock(), createElementBlock("tr", {
				key: pkg.name,
				class: "border-b border-slate-200 dark:border-slate-700"
			}, [
				createBaseVNode("td", _hoisted_18$29, toDisplayString(pkg.name), 1),
				createBaseVNode("td", _hoisted_19$25, toDisplayString(pkg.sales), 1),
				createBaseVNode("td", _hoisted_20$25, "KSh " + toDisplayString($options.formatNumber(pkg.revenue)), 1),
				createBaseVNode("td", _hoisted_21$24, "KSh " + toDisplayString($options.formatNumber(pkg.profit)), 1),
				createBaseVNode("td", _hoisted_22$24, [createBaseVNode("span", { class: normalizeClass(["px-2 py-1 rounded-full font-medium", pkg.margin >= 50 ? "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400" : pkg.margin >= 30 ? "bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400" : "bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400"]) }, toDisplayString(pkg.margin) + "% ", 3)])
			]);
		}), 128))])])]))])
	]);
}
var FinancialAnalytics_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$35, [["render", _sfc_render$35]]);
var _sfc_main$34 = {
	name: "RFMSegmentation",
	props: {
		segments: {
			type: Array,
			default: () => []
		},
		summary: {
			type: Object,
			default: () => ({})
		},
		loading: {
			type: Boolean,
			default: false
		}
	},
	computed: { topCustomers() {
		return this.segments.slice(0, 10).sort((a, b) => b.rfm_score - a.rfm_score);
	} },
	methods: {
		getSegmentStyle(segment) {
			return {
				"Champions": "bg-blue-50 dark:bg-blue-500/10 border-blue-200 dark:border-blue-500/20 text-blue-700 dark:text-blue-400",
				"Loyal": "bg-emerald-50 dark:bg-emerald-500/10 border-emerald-200 dark:border-emerald-500/20 text-emerald-700 dark:text-emerald-400",
				"New": "bg-purple-50 dark:bg-purple-500/10 border-purple-200 dark:border-purple-500/20 text-purple-700 dark:text-purple-400",
				"At Risk": "bg-amber-50 dark:bg-amber-500/10 border-amber-200 dark:border-amber-500/20 text-amber-700 dark:text-amber-400",
				"Lost": "bg-red-50 dark:bg-red-500/10 border-red-200 dark:border-red-500/20 text-red-700 dark:text-red-400",
				"Potential": "bg-cyan-50 dark:bg-cyan-500/10 border-cyan-200 dark:border-cyan-500/20 text-cyan-700 dark:text-cyan-400"
			}[segment] || "bg-slate-50 dark:bg-slate-700 border-slate-200 dark:border-slate-600";
		},
		getSegmentDot(segment) {
			return {
				"Champions": "bg-blue-500",
				"Loyal": "bg-emerald-500",
				"New": "bg-purple-500",
				"At Risk": "bg-amber-500",
				"Lost": "bg-red-500",
				"Potential": "bg-cyan-500"
			}[segment] || "bg-slate-500";
		},
		getSegmentBadge(segment) {
			return {
				"Champions": "bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400",
				"Loyal": "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400",
				"New": "bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400",
				"At Risk": "bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400",
				"Lost": "bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400",
				"Potential": "bg-cyan-100 dark:bg-cyan-500/20 text-cyan-700 dark:text-cyan-400"
			}[segment] || "bg-slate-100 dark:bg-slate-700";
		},
		formatNumber(num) {
			return new Intl.NumberFormat().format(num);
		}
	}
};
var _hoisted_1$34 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5" };
var _hoisted_2$34 = {
	key: 0,
	class: "text-center py-8 text-slate-400"
};
var _hoisted_3$34 = { key: 1 };
var _hoisted_4$34 = { class: "grid grid-cols-2 md:grid-cols-3 gap-3 mb-4" };
var _hoisted_5$34 = { class: "flex items-center gap-2 mb-1" };
var _hoisted_6$34 = { class: "text-xs font-medium" };
var _hoisted_7$34 = { class: "text-xl font-bold" };
var _hoisted_8$33 = { class: "text-xs opacity-75 mt-1" };
var _hoisted_9$31 = { class: "mt-4" };
var _hoisted_10$29 = { class: "overflow-x-auto" };
var _hoisted_11$28 = { class: "w-full text-xs" };
var _hoisted_12$28 = { class: "p-2 text-slate-900 dark:text-white" };
var _hoisted_13$28 = { class: "p-2 text-center" };
var _hoisted_14$28 = { class: "p-2 text-center text-slate-900 dark:text-white" };
var _hoisted_15$28 = { class: "p-2 text-center text-slate-900 dark:text-white" };
var _hoisted_16$28 = { class: "p-2 text-center text-slate-900 dark:text-white" };
var _hoisted_17$28 = { class: "p-2 text-center" };
var _hoisted_18$28 = { class: "font-bold text-blue-600 dark:text-blue-400" };
function _sfc_render$34(_ctx, _cache, $props, $setup, $data, $options) {
	return openBlock(), createElementBlock("div", _hoisted_1$34, [_cache[2] || (_cache[2] = createStaticVNode("<div class=\"flex items-center justify-between mb-4\"><div class=\"flex items-center gap-2\"><svg class=\"w-5 h-5 text-indigo-500\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z\"></path></svg><h3 class=\"text-sm font-medium text-slate-900 dark:text-white\">Customer Segmentation (RFM)</h3></div></div>", 1)), $props.loading ? (openBlock(), createElementBlock("div", _hoisted_2$34, "Loading...")) : (openBlock(), createElementBlock("div", _hoisted_3$34, [createBaseVNode("div", _hoisted_4$34, [(openBlock(true), createElementBlock(Fragment, null, renderList($props.summary, (data, segment) => {
		return openBlock(), createElementBlock("div", {
			key: segment,
			class: normalizeClass(["p-3 rounded-lg border", $options.getSegmentStyle(segment)])
		}, [
			createBaseVNode("div", _hoisted_5$34, [createBaseVNode("div", { class: normalizeClass(["w-2 h-2 rounded-full", $options.getSegmentDot(segment)]) }, null, 2), createBaseVNode("span", _hoisted_6$34, toDisplayString(segment), 1)]),
			createBaseVNode("p", _hoisted_7$34, toDisplayString(data.count), 1),
			createBaseVNode("p", _hoisted_8$33, "KSh " + toDisplayString($options.formatNumber(data.total_value)), 1)
		], 2);
	}), 128))]), createBaseVNode("div", _hoisted_9$31, [_cache[1] || (_cache[1] = createBaseVNode("h4", { class: "text-xs font-medium text-slate-600 dark:text-slate-400 mb-2" }, "Top Customers by RFM Score", -1)), createBaseVNode("div", _hoisted_10$29, [createBaseVNode("table", _hoisted_11$28, [_cache[0] || (_cache[0] = createBaseVNode("thead", { class: "border-b border-slate-200 dark:border-slate-700" }, [createBaseVNode("tr", null, [
		createBaseVNode("th", { class: "text-left p-2 text-slate-600 dark:text-slate-400" }, "Customer"),
		createBaseVNode("th", { class: "text-center p-2 text-slate-600 dark:text-slate-400" }, "Segment"),
		createBaseVNode("th", { class: "text-center p-2 text-slate-600 dark:text-slate-400" }, "Recency"),
		createBaseVNode("th", { class: "text-center p-2 text-slate-600 dark:text-slate-400" }, "Frequency"),
		createBaseVNode("th", { class: "text-center p-2 text-slate-600 dark:text-slate-400" }, "Monetary"),
		createBaseVNode("th", { class: "text-center p-2 text-slate-600 dark:text-slate-400" }, "Score")
	])], -1)), createBaseVNode("tbody", null, [(openBlock(true), createElementBlock(Fragment, null, renderList($options.topCustomers, (customer) => {
		return openBlock(), createElementBlock("tr", {
			key: customer.user_id,
			class: "border-b border-slate-200 dark:border-slate-700"
		}, [
			createBaseVNode("td", _hoisted_12$28, toDisplayString(customer.username), 1),
			createBaseVNode("td", _hoisted_13$28, [createBaseVNode("span", { class: normalizeClass(["px-2 py-1 rounded-full text-xs", $options.getSegmentBadge(customer.segment)]) }, toDisplayString(customer.segment), 3)]),
			createBaseVNode("td", _hoisted_14$28, toDisplayString(customer.recency) + "d", 1),
			createBaseVNode("td", _hoisted_15$28, toDisplayString(customer.frequency), 1),
			createBaseVNode("td", _hoisted_16$28, toDisplayString($options.formatNumber(customer.monetary)), 1),
			createBaseVNode("td", _hoisted_17$28, [createBaseVNode("span", _hoisted_18$28, toDisplayString(customer.rfm_score), 1)])
		]);
	}), 128))])])])])]))]);
}
var RFMSegmentation_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$34, [["render", _sfc_render$34]]);
var _sfc_main$33 = {
	name: "CohortAnalysis",
	props: {
		data: {
			type: Array,
			default: () => []
		},
		loading: {
			type: Boolean,
			default: false
		}
	},
	computed: { cohorts() {
		return this.data;
	} },
	methods: { getHeatmapColor(rate) {
		if (rate >= 75) return "#3b82f6";
		if (rate >= 50) return "#10b981";
		if (rate >= 25) return "#f59e0b";
		return "#ef4444";
	} }
};
var _hoisted_1$33 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5" };
var _hoisted_2$33 = {
	key: 0,
	class: "text-center py-8 text-slate-400"
};
var _hoisted_3$33 = {
	key: 1,
	class: "overflow-x-auto"
};
var _hoisted_4$33 = { class: "w-full text-xs" };
var _hoisted_5$33 = { class: "border-b border-slate-200 dark:border-slate-700" };
var _hoisted_6$33 = { class: "p-2 font-medium text-slate-900 dark:text-white" };
var _hoisted_7$33 = { class: "p-2 text-center text-slate-900 dark:text-white" };
function _sfc_render$33(_ctx, _cache, $props, $setup, $data, $options) {
	return openBlock(), createElementBlock("div", _hoisted_1$33, [
		_cache[2] || (_cache[2] = createStaticVNode("<div class=\"flex items-center justify-between mb-4\"><div class=\"flex items-center gap-2\"><svg class=\"w-5 h-5 text-purple-500\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z\"></path></svg><h3 class=\"text-sm font-medium text-slate-900 dark:text-white\">Cohort Retention Analysis</h3></div></div>", 1)),
		$props.loading ? (openBlock(), createElementBlock("div", _hoisted_2$33, "Loading...")) : (openBlock(), createElementBlock("div", _hoisted_3$33, [createBaseVNode("table", _hoisted_4$33, [createBaseVNode("thead", null, [createBaseVNode("tr", _hoisted_5$33, [
			_cache[0] || (_cache[0] = createBaseVNode("th", { class: "text-left p-2 text-slate-600 dark:text-slate-400" }, "Cohort", -1)),
			_cache[1] || (_cache[1] = createBaseVNode("th", { class: "text-center p-2 text-slate-600 dark:text-slate-400" }, "Size", -1)),
			(openBlock(), createElementBlock(Fragment, null, renderList(6, (i) => {
				return createBaseVNode("th", {
					key: i,
					class: "text-center p-2 text-slate-600 dark:text-slate-400"
				}, "M" + toDisplayString(i - 1), 1);
			}), 64))
		])]), createBaseVNode("tbody", null, [(openBlock(true), createElementBlock(Fragment, null, renderList($options.cohorts, (cohort) => {
			return openBlock(), createElementBlock("tr", {
				key: cohort.cohort,
				class: "border-b border-slate-200 dark:border-slate-700"
			}, [
				createBaseVNode("td", _hoisted_6$33, toDisplayString(cohort.cohort), 1),
				createBaseVNode("td", _hoisted_7$33, toDisplayString(cohort.size), 1),
				(openBlock(true), createElementBlock(Fragment, null, renderList(cohort.retention, (retention) => {
					return openBlock(), createElementBlock("td", {
						key: retention.month,
						class: "p-2 text-center"
					}, [createBaseVNode("div", {
						class: "rounded px-2 py-1 font-medium",
						style: normalizeStyle({
							backgroundColor: $options.getHeatmapColor(retention.rate),
							color: retention.rate > 50 ? "#fff" : "#1e293b"
						})
					}, toDisplayString(retention.rate) + "% ", 5)]);
				}), 128))
			]);
		}), 128))])])])),
		_cache[3] || (_cache[3] = createStaticVNode("<div class=\"mt-4 flex items-center gap-4 text-xs text-slate-600 dark:text-slate-400\"><span>Retention Rate:</span><div class=\"flex items-center gap-2\"><div class=\"w-4 h-4 rounded\" style=\"background-color:#ef4444;\"></div><span>0-25%</span></div><div class=\"flex items-center gap-2\"><div class=\"w-4 h-4 rounded\" style=\"background-color:#f59e0b;\"></div><span>25-50%</span></div><div class=\"flex items-center gap-2\"><div class=\"w-4 h-4 rounded\" style=\"background-color:#10b981;\"></div><span>50-75%</span></div><div class=\"flex items-center gap-2\"><div class=\"w-4 h-4 rounded\" style=\"background-color:#3b82f6;\"></div><span>75-100%</span></div></div>", 1))
	]);
}
var CohortAnalysis_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$33, [["render", _sfc_render$33]]);
var _sfc_main$32 = {
	name: "FunnelAnalysis",
	props: {
		data: {
			type: Object,
			default: () => ({
				stages: [],
				conversion_rate: 0,
				biggest_dropoff: "",
				total_signups: 0,
				repeat_customers: 0
			})
		},
		loading: {
			type: Boolean,
			default: false
		}
	},
	methods: {
		getStageColor(idx) {
			return [
				"bg-blue-500 text-white",
				"bg-purple-500 text-white",
				"bg-cyan-500 text-white",
				"bg-emerald-500 text-white",
				"bg-amber-500 text-white",
				"bg-rose-500 text-white"
			][idx] || "bg-slate-500 text-white";
		},
		getBarColor(idx) {
			return [
				"bg-blue-500",
				"bg-purple-500",
				"bg-cyan-500",
				"bg-emerald-500",
				"bg-amber-500",
				"bg-rose-500"
			][idx] || "bg-slate-500";
		},
		getRateColor(rate) {
			if (rate >= 75) return "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400";
			if (rate >= 50) return "bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400";
			if (rate >= 25) return "bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400";
			return "bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400";
		}
	}
};
var _hoisted_1$32 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5" };
var _hoisted_2$32 = { class: "flex items-center justify-between mb-4" };
var _hoisted_3$32 = { class: "text-right" };
var _hoisted_4$32 = { class: "text-lg font-bold text-emerald-600 dark:text-emerald-400" };
var _hoisted_5$32 = {
	key: 0,
	class: "text-center py-8 text-slate-400"
};
var _hoisted_6$32 = {
	key: 1,
	class: "space-y-3"
};
var _hoisted_7$32 = { class: "flex items-center gap-4" };
var _hoisted_8$32 = { class: "flex-1" };
var _hoisted_9$30 = { class: "flex items-center justify-between mb-1" };
var _hoisted_10$28 = { class: "text-sm font-medium text-slate-900 dark:text-white" };
var _hoisted_11$27 = { class: "flex items-center gap-3" };
var _hoisted_12$27 = { class: "text-sm font-bold text-slate-900 dark:text-white" };
var _hoisted_13$27 = { class: "h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden" };
var _hoisted_14$27 = {
	key: 0,
	class: "mt-1 flex items-center gap-1 text-xs text-red-600 dark:text-red-400"
};
var _hoisted_15$27 = {
	key: 0,
	class: "ml-4 h-4 w-0.5 bg-slate-300 dark:bg-slate-600"
};
var _hoisted_16$27 = { class: "mt-6 p-4 bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 rounded-lg" };
var _hoisted_17$27 = { class: "flex items-start gap-3" };
var _hoisted_18$27 = { class: "text-xs text-amber-700 dark:text-amber-500 mt-1" };
var _hoisted_19$24 = { class: "mt-4 grid grid-cols-2 gap-4" };
var _hoisted_20$24 = { class: "text-center p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg" };
var _hoisted_21$23 = { class: "text-xl font-bold text-slate-900 dark:text-white" };
var _hoisted_22$23 = { class: "text-center p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg" };
var _hoisted_23$23 = { class: "text-xl font-bold text-emerald-600 dark:text-emerald-400" };
function _sfc_render$32(_ctx, _cache, $props, $setup, $data, $options) {
	return openBlock(), createElementBlock("div", _hoisted_1$32, [
		createBaseVNode("div", _hoisted_2$32, [_cache[1] || (_cache[1] = createBaseVNode("div", { class: "flex items-center gap-2" }, [createBaseVNode("svg", {
			class: "w-5 h-5 text-rose-500",
			fill: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", { d: "M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z" })]), createBaseVNode("h3", { class: "text-sm font-medium text-slate-900 dark:text-white" }, "Conversion Funnel Analysis")], -1)), createBaseVNode("div", _hoisted_3$32, [_cache[0] || (_cache[0] = createBaseVNode("p", { class: "text-xs text-slate-600 dark:text-slate-400" }, "Overall Conversion", -1)), createBaseVNode("p", _hoisted_4$32, toDisplayString($props.data.conversion_rate) + "%", 1)])]),
		$props.loading ? (openBlock(), createElementBlock("div", _hoisted_5$32, "Loading...")) : (openBlock(), createElementBlock("div", _hoisted_6$32, [(openBlock(true), createElementBlock(Fragment, null, renderList($props.data.stages, (stage, idx) => {
			return openBlock(), createElementBlock("div", {
				key: idx,
				class: "relative"
			}, [createBaseVNode("div", _hoisted_7$32, [createBaseVNode("div", { class: normalizeClass(["w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold", $options.getStageColor(idx)]) }, toDisplayString(idx + 1), 3), createBaseVNode("div", _hoisted_8$32, [
				createBaseVNode("div", _hoisted_9$30, [createBaseVNode("span", _hoisted_10$28, toDisplayString(stage.name), 1), createBaseVNode("div", _hoisted_11$27, [createBaseVNode("span", _hoisted_12$27, toDisplayString(stage.users), 1), createBaseVNode("span", { class: normalizeClass(["text-xs px-2 py-1 rounded-full", $options.getRateColor(stage.rate)]) }, toDisplayString(stage.rate) + "% ", 3)])]),
				createBaseVNode("div", _hoisted_13$27, [createBaseVNode("div", {
					class: normalizeClass(["h-full transition-all duration-500", $options.getBarColor(idx)]),
					style: normalizeStyle({ width: stage.rate + "%" })
				}, null, 6)]),
				stage.dropoff > 0 ? (openBlock(), createElementBlock("div", _hoisted_14$27, [_cache[2] || (_cache[2] = createBaseVNode("svg", {
					class: "w-3 h-3",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M16 18l2.29-2.29-4.88-4.88-4 4L2 7.41 3.41 6l6 6 4-4 6.3 6.29L22 12v6z" })], -1)), createBaseVNode("span", null, toDisplayString(stage.dropoff) + " users dropped", 1)])) : createCommentVNode("", true)
			])]), idx < $props.data.stages.length - 1 ? (openBlock(), createElementBlock("div", _hoisted_15$27)) : createCommentVNode("", true)]);
		}), 128))])),
		createBaseVNode("div", _hoisted_16$27, [createBaseVNode("div", _hoisted_17$27, [_cache[6] || (_cache[6] = createBaseVNode("svg", {
			class: "w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5",
			fill: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" })], -1)), createBaseVNode("div", null, [_cache[5] || (_cache[5] = createBaseVNode("p", { class: "text-sm font-medium text-amber-900 dark:text-amber-400" }, "Biggest Drop-off Point", -1)), createBaseVNode("p", _hoisted_18$27, [
			_cache[3] || (_cache[3] = createTextVNode(" Most users are dropping at ", -1)),
			createBaseVNode("strong", null, toDisplayString($props.data.biggest_dropoff), 1),
			_cache[4] || (_cache[4] = createTextVNode(". Focus optimization efforts here. ", -1))
		])])])]),
		createBaseVNode("div", _hoisted_19$24, [createBaseVNode("div", _hoisted_20$24, [_cache[7] || (_cache[7] = createBaseVNode("p", { class: "text-xs text-slate-600 dark:text-slate-400" }, "Total Signups", -1)), createBaseVNode("p", _hoisted_21$23, toDisplayString($props.data.total_signups), 1)]), createBaseVNode("div", _hoisted_22$23, [_cache[8] || (_cache[8] = createBaseVNode("p", { class: "text-xs text-slate-600 dark:text-slate-400" }, "Repeat Customers", -1)), createBaseVNode("p", _hoisted_23$23, toDisplayString($props.data.repeat_customers), 1)])])
	]);
}
var FunnelAnalysis_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$32, [["render", _sfc_render$32]]);
var _sfc_main$31 = {
	name: "ChurnPrediction",
	props: {
		data: {
			type: Object,
			default: () => ({
				at_risk_users: [],
				summary: {},
				churn_rate: 0
			})
		},
		loading: {
			type: Boolean,
			default: false
		}
	},
	computed: { topAtRisk() {
		return this.data.at_risk_users?.slice(0, 10) || [];
	} },
	methods: {
		getRiskBadge(risk) {
			return {
				"high": "bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400",
				"medium": "bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400",
				"low": "bg-yellow-100 dark:bg-yellow-500/20 text-yellow-700 dark:text-yellow-400"
			}[risk] || "bg-slate-100 dark:bg-slate-700";
		},
		getRiskColor(probability) {
			if (probability >= 70) return "text-red-600 dark:text-red-400";
			if (probability >= 50) return "text-amber-600 dark:text-amber-400";
			return "text-yellow-600 dark:text-yellow-400";
		}
	}
};
var _hoisted_1$31 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5" };
var _hoisted_2$31 = { class: "flex items-center justify-between mb-4" };
var _hoisted_3$31 = { class: "text-right" };
var _hoisted_4$31 = { class: "text-lg font-bold text-red-600 dark:text-red-400" };
var _hoisted_5$31 = {
	key: 0,
	class: "text-center py-8 text-slate-400"
};
var _hoisted_6$31 = { key: 1 };
var _hoisted_7$31 = { class: "grid grid-cols-3 gap-3 mb-4" };
var _hoisted_8$31 = { class: "p-3 rounded-lg bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20" };
var _hoisted_9$29 = { class: "text-2xl font-bold text-red-700 dark:text-red-300" };
var _hoisted_10$27 = { class: "p-3 rounded-lg bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20" };
var _hoisted_11$26 = { class: "text-2xl font-bold text-amber-700 dark:text-amber-300" };
var _hoisted_12$26 = { class: "p-3 rounded-lg bg-yellow-50 dark:bg-yellow-500/10 border border-yellow-200 dark:border-yellow-500/20" };
var _hoisted_13$26 = { class: "text-2xl font-bold text-yellow-700 dark:text-yellow-300" };
var _hoisted_14$26 = { class: "overflow-x-auto" };
var _hoisted_15$26 = { class: "w-full text-xs" };
var _hoisted_16$26 = { class: "p-2 text-slate-900 dark:text-white" };
var _hoisted_17$26 = { class: "p-2 text-center text-slate-900 dark:text-white" };
var _hoisted_18$26 = { class: "p-2 text-center text-slate-900 dark:text-white" };
var _hoisted_19$23 = { class: "p-2 text-center" };
var _hoisted_20$23 = { class: "p-2 text-center" };
function _sfc_render$31(_ctx, _cache, $props, $setup, $data, $options) {
	return openBlock(), createElementBlock("div", _hoisted_1$31, [createBaseVNode("div", _hoisted_2$31, [_cache[1] || (_cache[1] = createBaseVNode("div", { class: "flex items-center gap-2" }, [createBaseVNode("svg", {
		class: "w-5 h-5 text-red-500",
		fill: "currentColor",
		viewBox: "0 0 24 24"
	}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" })]), createBaseVNode("h3", { class: "text-sm font-medium text-slate-900 dark:text-white" }, "Churn Prediction")], -1)), createBaseVNode("div", _hoisted_3$31, [_cache[0] || (_cache[0] = createBaseVNode("p", { class: "text-xs text-slate-600 dark:text-slate-400" }, "Churn Rate", -1)), createBaseVNode("p", _hoisted_4$31, toDisplayString($props.data.churn_rate) + "%", 1)])]), $props.loading ? (openBlock(), createElementBlock("div", _hoisted_5$31, "Loading...")) : (openBlock(), createElementBlock("div", _hoisted_6$31, [createBaseVNode("div", _hoisted_7$31, [
		createBaseVNode("div", _hoisted_8$31, [_cache[2] || (_cache[2] = createBaseVNode("p", { class: "text-xs text-red-600 dark:text-red-400 mb-1" }, "High Risk", -1)), createBaseVNode("p", _hoisted_9$29, toDisplayString($props.data.summary?.high_risk || 0), 1)]),
		createBaseVNode("div", _hoisted_10$27, [_cache[3] || (_cache[3] = createBaseVNode("p", { class: "text-xs text-amber-600 dark:text-amber-400 mb-1" }, "Medium Risk", -1)), createBaseVNode("p", _hoisted_11$26, toDisplayString($props.data.summary?.medium_risk || 0), 1)]),
		createBaseVNode("div", _hoisted_12$26, [_cache[4] || (_cache[4] = createBaseVNode("p", { class: "text-xs text-yellow-600 dark:text-yellow-400 mb-1" }, "Low Risk", -1)), createBaseVNode("p", _hoisted_13$26, toDisplayString($props.data.summary?.low_risk || 0), 1)])
	]), createBaseVNode("div", _hoisted_14$26, [createBaseVNode("table", _hoisted_15$26, [_cache[5] || (_cache[5] = createBaseVNode("thead", { class: "border-b border-slate-200 dark:border-slate-700" }, [createBaseVNode("tr", null, [
		createBaseVNode("th", { class: "text-left p-2 text-slate-600 dark:text-slate-400" }, "User"),
		createBaseVNode("th", { class: "text-center p-2 text-slate-600 dark:text-slate-400" }, "Inactive Days"),
		createBaseVNode("th", { class: "text-center p-2 text-slate-600 dark:text-slate-400" }, "Purchases"),
		createBaseVNode("th", { class: "text-center p-2 text-slate-600 dark:text-slate-400" }, "Risk"),
		createBaseVNode("th", { class: "text-center p-2 text-slate-600 dark:text-slate-400" }, "Probability")
	])], -1)), createBaseVNode("tbody", null, [(openBlock(true), createElementBlock(Fragment, null, renderList($options.topAtRisk, (user) => {
		return openBlock(), createElementBlock("tr", {
			key: user.user_id,
			class: "border-b border-slate-200 dark:border-slate-700"
		}, [
			createBaseVNode("td", _hoisted_16$26, toDisplayString(user.username), 1),
			createBaseVNode("td", _hoisted_17$26, toDisplayString(user.days_inactive), 1),
			createBaseVNode("td", _hoisted_18$26, toDisplayString(user.total_purchases), 1),
			createBaseVNode("td", _hoisted_19$23, [createBaseVNode("span", { class: normalizeClass(["px-2 py-1 rounded-full text-xs font-medium", $options.getRiskBadge(user.risk_level)]) }, toDisplayString(user.risk_level), 3)]),
			createBaseVNode("td", _hoisted_20$23, [createBaseVNode("span", { class: normalizeClass(["font-bold", $options.getRiskColor(user.churn_probability)]) }, toDisplayString(user.churn_probability) + "% ", 3)])
		]);
	}), 128))])])])]))]);
}
var ChurnPrediction_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$31, [["render", _sfc_render$31]]);
var _sfc_main$30 = {
	name: "RevenueForecast",
	components: { apexchart: m },
	props: {
		data: {
			type: Object,
			default: () => ({
				historical: [],
				forecast: [],
				avg_monthly_growth: 0,
				trend: "upward"
			})
		},
		loading: {
			type: Boolean,
			default: false
		}
	},
	computed: {
		chartData() {
			return [...this.data.historical || [], ...this.data.forecast || []];
		},
		chartSeries() {
			return [{
				name: "Historical",
				data: (this.data.historical || []).map((item) => ({
					x: item.month,
					y: item.revenue
				}))
			}, {
				name: "Forecast",
				data: (this.data.forecast || []).map((item) => ({
					x: item.month,
					y: item.predicted_revenue
				}))
			}];
		},
		chartOptions() {
			return {
				chart: {
					type: "line",
					toolbar: { show: false },
					zoom: { enabled: false }
				},
				colors: ["#3b82f6", "#10b981"],
				stroke: {
					width: [3, 3],
					dashArray: [0, 5]
				},
				dataLabels: { enabled: false },
				xaxis: {
					type: "category",
					labels: { style: {
						colors: "#94a3b8",
						fontSize: "10px"
					} }
				},
				yaxis: { labels: {
					style: {
						colors: "#94a3b8",
						fontSize: "10px"
					},
					formatter: (v) => `${this.formatNumber(v)}`
				} },
				grid: {
					borderColor: "#e2e8f0",
					strokeDashArray: 3
				},
				tooltip: { theme: "dark" },
				legend: {
					position: "top",
					fontSize: "11px"
				}
			};
		}
	},
	methods: { formatNumber(num) {
		return new Intl.NumberFormat().format(Math.round(num));
	} }
};
var _hoisted_1$30 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5" };
var _hoisted_2$30 = { class: "flex items-center justify-between mb-4" };
var _hoisted_3$30 = { class: "flex items-center gap-2" };
var _hoisted_4$30 = {
	key: 0,
	d: "M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"
};
var _hoisted_5$30 = {
	key: 1,
	d: "M16 18l2.29-2.29-4.88-4.88-4 4L2 7.41 3.41 6l6 6 4-4 6.3 6.29L22 12v6z"
};
var _hoisted_6$30 = {
	key: 0,
	class: "text-center py-8 text-slate-400"
};
var _hoisted_7$30 = { key: 1 };
var _hoisted_8$30 = {
	key: 0,
	class: "h-64 mb-4"
};
var _hoisted_9$28 = { class: "mt-4" };
var _hoisted_10$26 = { class: "grid grid-cols-2 md:grid-cols-3 gap-2" };
var _hoisted_11$25 = { class: "text-xs text-slate-600 dark:text-slate-400" };
var _hoisted_12$25 = { class: "text-lg font-bold text-slate-900 dark:text-white" };
var _hoisted_13$25 = { class: "flex items-center gap-1 mt-1" };
var _hoisted_14$25 = { class: "flex-1 h-1 bg-slate-200 dark:bg-slate-600 rounded-full overflow-hidden" };
var _hoisted_15$25 = { class: "text-xs text-slate-500 dark:text-slate-400" };
var _hoisted_16$25 = { class: "mt-4 p-3 bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/20 rounded-lg" };
var _hoisted_17$25 = { class: "flex items-center justify-between" };
var _hoisted_18$25 = { class: "text-sm font-bold text-blue-700 dark:text-blue-300" };
function _sfc_render$30(_ctx, _cache, $props, $setup, $data, $options) {
	const _component_apexchart = resolveComponent("apexchart");
	return openBlock(), createElementBlock("div", _hoisted_1$30, [createBaseVNode("div", _hoisted_2$30, [_cache[0] || (_cache[0] = createBaseVNode("div", { class: "flex items-center gap-2" }, [createBaseVNode("svg", {
		class: "w-5 h-5 text-blue-500",
		fill: "currentColor",
		viewBox: "0 0 24 24"
	}, [createBaseVNode("path", { d: "M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z" })]), createBaseVNode("h3", { class: "text-sm font-medium text-slate-900 dark:text-white" }, "Revenue Forecast")], -1)), createBaseVNode("div", _hoisted_3$30, [(openBlock(), createElementBlock("svg", {
		class: normalizeClass(["w-4 h-4", $props.data.trend === "upward" ? "text-emerald-500" : "text-red-500"]),
		fill: "currentColor",
		viewBox: "0 0 24 24"
	}, [$props.data.trend === "upward" ? (openBlock(), createElementBlock("path", _hoisted_4$30)) : (openBlock(), createElementBlock("path", _hoisted_5$30))], 2)), createBaseVNode("span", { class: normalizeClass(["text-xs font-medium", $props.data.trend === "upward" ? "text-emerald-600 dark:text-emerald-400" : "text-red-600 dark:text-red-400"]) }, toDisplayString($props.data.trend === "upward" ? "Growing" : "Declining"), 3)])]), $props.loading ? (openBlock(), createElementBlock("div", _hoisted_6$30, "Loading...")) : (openBlock(), createElementBlock("div", _hoisted_7$30, [
		$options.chartData.length > 0 ? (openBlock(), createElementBlock("div", _hoisted_8$30, [createVNode(_component_apexchart, {
			type: "line",
			height: "100%",
			options: $options.chartOptions,
			series: $options.chartSeries
		}, null, 8, ["options", "series"])])) : createCommentVNode("", true),
		createBaseVNode("div", _hoisted_9$28, [_cache[1] || (_cache[1] = createBaseVNode("h4", { class: "text-xs font-medium text-slate-600 dark:text-slate-400 mb-2" }, "6-Month Forecast", -1)), createBaseVNode("div", _hoisted_10$26, [(openBlock(true), createElementBlock(Fragment, null, renderList($props.data.forecast, (item) => {
			return openBlock(), createElementBlock("div", {
				key: item.month,
				class: "p-3 rounded-lg bg-slate-50 dark:bg-slate-700/50"
			}, [
				createBaseVNode("p", _hoisted_11$25, toDisplayString(item.month), 1),
				createBaseVNode("p", _hoisted_12$25, "KSh " + toDisplayString($options.formatNumber(item.predicted_revenue)), 1),
				createBaseVNode("div", _hoisted_13$25, [createBaseVNode("div", _hoisted_14$25, [createBaseVNode("div", {
					class: "h-full bg-blue-500",
					style: normalizeStyle({ width: item.confidence + "%" })
				}, null, 4)]), createBaseVNode("span", _hoisted_15$25, toDisplayString(item.confidence) + "%", 1)])
			]);
		}), 128))])]),
		createBaseVNode("div", _hoisted_16$25, [createBaseVNode("div", _hoisted_17$25, [_cache[2] || (_cache[2] = createBaseVNode("span", { class: "text-xs text-blue-600 dark:text-blue-400" }, "Avg Monthly Growth", -1)), createBaseVNode("span", _hoisted_18$25, "KSh " + toDisplayString($options.formatNumber($props.data.avg_monthly_growth)), 1)])])
	]))]);
}
var RevenueForecast_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$30, [["render", _sfc_render$30]]);
var _sfc_main$29 = {
	name: "NetworkAnalytics",
	props: {
		data: {
			type: Object,
			default: () => ({
				locations: [],
				overall: {}
			})
		},
		loading: {
			type: Boolean,
			default: false
		}
	},
	methods: {
		getHealthDot(status) {
			return {
				"healthy": "bg-emerald-500",
				"warning": "bg-amber-500",
				"critical": "bg-red-500"
			}[status] || "bg-slate-500";
		},
		getHealthBadge(status) {
			return {
				"healthy": "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400",
				"warning": "bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400",
				"critical": "bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400"
			}[status] || "bg-slate-100 dark:bg-slate-700";
		},
		getLocationBorder(status) {
			return {
				"healthy": "border-emerald-200 dark:border-emerald-500/20 bg-emerald-50/50 dark:bg-emerald-500/5",
				"warning": "border-amber-200 dark:border-amber-500/20 bg-amber-50/50 dark:bg-amber-500/5",
				"critical": "border-red-200 dark:border-red-500/20 bg-red-50/50 dark:bg-red-500/5"
			}[status] || "border-slate-200 dark:border-slate-700";
		},
		getUtilizationColor(utilization) {
			if (utilization > 90) return "text-red-600 dark:text-red-400";
			if (utilization > 70) return "text-amber-600 dark:text-amber-400";
			return "text-emerald-600 dark:text-emerald-400";
		},
		getUtilizationBar(utilization) {
			if (utilization > 90) return "bg-red-500";
			if (utilization > 70) return "bg-amber-500";
			return "bg-emerald-500";
		}
	}
};
var _hoisted_1$29 = { class: "space-y-4" };
var _hoisted_2$29 = { class: "grid grid-cols-1 md:grid-cols-4 gap-4" };
var _hoisted_3$29 = { class: "bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700" };
var _hoisted_4$29 = { class: "text-2xl font-bold text-slate-900 dark:text-white" };
var _hoisted_5$29 = { class: "bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700" };
var _hoisted_6$29 = { class: "text-2xl font-bold text-slate-900 dark:text-white" };
var _hoisted_7$29 = { class: "bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700" };
var _hoisted_8$29 = { class: "text-2xl font-bold text-slate-900 dark:text-white" };
var _hoisted_9$27 = { class: "bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700" };
var _hoisted_10$25 = { class: "text-2xl font-bold text-slate-900 dark:text-white" };
var _hoisted_11$24 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5" };
var _hoisted_12$24 = {
	key: 0,
	class: "text-center py-8 text-slate-400"
};
var _hoisted_13$24 = {
	key: 1,
	class: "space-y-2"
};
var _hoisted_14$24 = { class: "flex items-center justify-between mb-2" };
var _hoisted_15$24 = { class: "flex items-center gap-3" };
var _hoisted_16$24 = { class: "text-sm font-medium text-slate-900 dark:text-white" };
var _hoisted_17$24 = { class: "text-xs text-slate-500 dark:text-slate-400" };
var _hoisted_18$24 = { class: "grid grid-cols-4 gap-4 mt-3" };
var _hoisted_19$22 = { class: "text-sm font-bold text-slate-900 dark:text-white" };
var _hoisted_20$22 = { class: "text-sm font-bold text-slate-900 dark:text-white" };
var _hoisted_21$22 = { class: "text-sm font-bold text-slate-900 dark:text-white" };
var _hoisted_22$22 = { class: "mt-3 h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden" };
var _hoisted_23$22 = { class: "grid grid-cols-3 gap-4" };
var _hoisted_24$22 = { class: "bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-lg p-4" };
var _hoisted_25$22 = { class: "text-2xl font-bold text-emerald-700 dark:text-emerald-300" };
var _hoisted_26$22 = { class: "bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 rounded-lg p-4" };
var _hoisted_27$21 = { class: "text-2xl font-bold text-amber-700 dark:text-amber-300" };
var _hoisted_28$21 = { class: "bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 rounded-lg p-4" };
var _hoisted_29$21 = { class: "text-2xl font-bold text-red-700 dark:text-red-300" };
function _sfc_render$29(_ctx, _cache, $props, $setup, $data, $options) {
	return openBlock(), createElementBlock("div", _hoisted_1$29, [
		createBaseVNode("div", _hoisted_2$29, [
			createBaseVNode("div", _hoisted_3$29, [_cache[0] || (_cache[0] = createBaseVNode("div", { class: "flex items-center gap-2 mb-2" }, [createBaseVNode("svg", {
				class: "w-5 h-5 text-blue-500",
				fill: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", { d: "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" })]), createBaseVNode("span", { class: "text-xs text-slate-600 dark:text-slate-400" }, "Total Locations")], -1)), createBaseVNode("p", _hoisted_4$29, toDisplayString($props.data.overall?.total_locations || 0), 1)]),
			createBaseVNode("div", _hoisted_5$29, [_cache[1] || (_cache[1] = createBaseVNode("div", { class: "flex items-center gap-2 mb-2" }, [createBaseVNode("svg", {
				class: "w-5 h-5 text-emerald-500",
				fill: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" })]), createBaseVNode("span", { class: "text-xs text-slate-600 dark:text-slate-400" }, "Capacity")], -1)), createBaseVNode("p", _hoisted_6$29, toDisplayString($props.data.overall?.total_capacity || 0), 1)]),
			createBaseVNode("div", _hoisted_7$29, [_cache[2] || (_cache[2] = createBaseVNode("div", { class: "flex items-center gap-2 mb-2" }, [createBaseVNode("svg", {
				class: "w-5 h-5 text-purple-500",
				fill: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", { d: "M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z" })]), createBaseVNode("span", { class: "text-xs text-slate-600 dark:text-slate-400" }, "Active Sessions")], -1)), createBaseVNode("p", _hoisted_8$29, toDisplayString($props.data.overall?.total_active_sessions || 0), 1)]),
			createBaseVNode("div", _hoisted_9$27, [_cache[3] || (_cache[3] = createBaseVNode("div", { class: "flex items-center gap-2 mb-2" }, [createBaseVNode("svg", {
				class: "w-5 h-5 text-amber-500",
				fill: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", { d: "M3.5 18.49l6-6.01 4 4L22 6.92l-1.41-1.41-7.09 7.97-4-4L2 16.99z" })]), createBaseVNode("span", { class: "text-xs text-slate-600 dark:text-slate-400" }, "Utilization")], -1)), createBaseVNode("p", _hoisted_10$25, toDisplayString($props.data.overall?.overall_utilization || 0) + "%", 1)])
		]),
		createBaseVNode("div", _hoisted_11$24, [_cache[8] || (_cache[8] = createBaseVNode("div", { class: "flex items-center gap-2 mb-4" }, [createBaseVNode("svg", {
			class: "w-5 h-5 text-cyan-500",
			fill: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" })]), createBaseVNode("h3", { class: "text-sm font-medium text-slate-900 dark:text-white" }, "Location Network Health")], -1)), $props.loading ? (openBlock(), createElementBlock("div", _hoisted_12$24, "Loading...")) : (openBlock(), createElementBlock("div", _hoisted_13$24, [(openBlock(true), createElementBlock(Fragment, null, renderList($props.data.locations, (location) => {
			return openBlock(), createElementBlock("div", {
				key: location.location_id,
				class: normalizeClass(["p-4 rounded-lg border transition-colors", $options.getLocationBorder(location.health_status)])
			}, [
				createBaseVNode("div", _hoisted_14$24, [createBaseVNode("div", _hoisted_15$24, [createBaseVNode("div", { class: normalizeClass(["w-3 h-3 rounded-full", $options.getHealthDot(location.health_status)]) }, null, 2), createBaseVNode("div", null, [createBaseVNode("p", _hoisted_16$24, toDisplayString(location.location_name), 1), createBaseVNode("p", _hoisted_17$24, toDisplayString(location.router_ip), 1)])]), createBaseVNode("span", { class: normalizeClass(["px-3 py-1 rounded-full text-xs font-medium", $options.getHealthBadge(location.health_status)]) }, toDisplayString(location.health_status), 3)]),
				createBaseVNode("div", _hoisted_18$24, [
					createBaseVNode("div", null, [_cache[4] || (_cache[4] = createBaseVNode("p", { class: "text-xs text-slate-600 dark:text-slate-400" }, "Active", -1)), createBaseVNode("p", _hoisted_19$22, toDisplayString(location.active_sessions), 1)]),
					createBaseVNode("div", null, [_cache[5] || (_cache[5] = createBaseVNode("p", { class: "text-xs text-slate-600 dark:text-slate-400" }, "Capacity", -1)), createBaseVNode("p", _hoisted_20$22, toDisplayString(location.max_capacity), 1)]),
					createBaseVNode("div", null, [_cache[6] || (_cache[6] = createBaseVNode("p", { class: "text-xs text-slate-600 dark:text-slate-400" }, "Utilization", -1)), createBaseVNode("p", { class: normalizeClass(["text-sm font-bold", $options.getUtilizationColor(location.utilization)]) }, toDisplayString(location.utilization) + "%", 3)]),
					createBaseVNode("div", null, [_cache[7] || (_cache[7] = createBaseVNode("p", { class: "text-xs text-slate-600 dark:text-slate-400" }, "Vouchers", -1)), createBaseVNode("p", _hoisted_21$22, toDisplayString(location.total_vouchers), 1)])
				]),
				createBaseVNode("div", _hoisted_22$22, [createBaseVNode("div", {
					class: normalizeClass(["h-full transition-all duration-500", $options.getUtilizationBar(location.utilization)]),
					style: normalizeStyle({ width: location.utilization + "%" })
				}, null, 6)])
			], 2);
		}), 128))]))]),
		createBaseVNode("div", _hoisted_23$22, [
			createBaseVNode("div", _hoisted_24$22, [_cache[9] || (_cache[9] = createBaseVNode("p", { class: "text-xs text-emerald-600 dark:text-emerald-400 mb-1" }, "Healthy", -1)), createBaseVNode("p", _hoisted_25$22, toDisplayString($props.data.overall?.healthy_locations || 0), 1)]),
			createBaseVNode("div", _hoisted_26$22, [_cache[10] || (_cache[10] = createBaseVNode("p", { class: "text-xs text-amber-600 dark:text-amber-400 mb-1" }, "Warning", -1)), createBaseVNode("p", _hoisted_27$21, toDisplayString($props.data.overall?.warning_locations || 0), 1)]),
			createBaseVNode("div", _hoisted_28$21, [_cache[11] || (_cache[11] = createBaseVNode("p", { class: "text-xs text-red-600 dark:text-red-400 mb-1" }, "Critical", -1)), createBaseVNode("p", _hoisted_29$21, toDisplayString($props.data.overall?.critical_locations || 0), 1)])
		])
	]);
}
var NetworkAnalytics_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$29, [["render", _sfc_render$29]]);
var _sfc_main$28 = {
	name: "DashboardBuilder",
	data() {
		return {
			activeWidgets: [],
			savedLayouts: [],
			showTemplates: false,
			widgetData: {},
			availableWidgets: [
				{
					id: 1,
					name: "Revenue",
					type: "revenue",
					size: "Medium",
					color: "bg-emerald-100 dark:bg-emerald-500/20",
					icon: "<svg class=\"w-6 h-6 text-emerald-600 dark:text-emerald-400\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z\"/></svg>"
				},
				{
					id: 2,
					name: "Users",
					type: "users",
					size: "Small",
					color: "bg-blue-100 dark:bg-blue-500/20",
					icon: "<svg class=\"w-6 h-6 text-blue-600 dark:text-blue-400\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z\"/></svg>"
				},
				{
					id: 3,
					name: "Sessions",
					type: "sessions",
					size: "Small",
					color: "bg-purple-100 dark:bg-purple-500/20",
					icon: "<svg class=\"w-6 h-6 text-purple-600 dark:text-purple-400\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z\"/></svg>"
				},
				{
					id: 4,
					name: "Packages",
					type: "packages",
					size: "Medium",
					color: "bg-cyan-100 dark:bg-cyan-500/20",
					icon: "<svg class=\"w-6 h-6 text-cyan-600 dark:text-cyan-400\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4z\"/></svg>"
				},
				{
					id: 5,
					name: "Locations",
					type: "locations",
					size: "Medium",
					color: "bg-rose-100 dark:bg-rose-500/20",
					icon: "<svg class=\"w-6 h-6 text-rose-600 dark:text-rose-400\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z\"/></svg>"
				},
				{
					id: 6,
					name: "Churn",
					type: "churn",
					size: "Small",
					color: "bg-red-100 dark:bg-red-500/20",
					icon: "<svg class=\"w-6 h-6 text-red-600 dark:text-red-400\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z\"/></svg>"
				}
			],
			templates: [
				{
					id: 1,
					name: "Executive Dashboard",
					description: "High-level overview for executives",
					widgets: [
						"Revenue",
						"Users",
						"Sessions"
					]
				},
				{
					id: 2,
					name: "Sales Dashboard",
					description: "Focus on revenue and packages",
					widgets: [
						"Revenue",
						"Packages",
						"Locations"
					]
				},
				{
					id: 3,
					name: "Operations Dashboard",
					description: "Monitor system health",
					widgets: [
						"Sessions",
						"Users",
						"Churn"
					]
				},
				{
					id: 4,
					name: "Complete Overview",
					description: "All key metrics",
					widgets: [
						"Revenue",
						"Users",
						"Sessions",
						"Packages",
						"Locations",
						"Churn"
					]
				}
			]
		};
	},
	mounted() {
		this.loadSavedLayouts();
		this.fetchWidgetData();
	},
	methods: {
		async fetchWidgetData() {
			try {
				const token = localStorage.getItem("access_token");
				const headers = { "Authorization": `Bearer ${token}` };
				const [metrics, packages, locations] = await Promise.all([
					fetch("https://srv.teralinkxwaves.uk/suapi/dashboard-metrics/", { headers }).then((r) => r.json()),
					fetch("https://srv.teralinkxwaves.uk/suapi/dashboard-metrics/package-sales/", { headers }).then((r) => r.json()),
					fetch("https://srv.teralinkxwaves.uk/suapi/dashboard-metrics/location-performance/", { headers }).then((r) => r.json())
				]);
				this.widgetData = {
					revenue: {
						total: metrics.totalRevenue,
						trend: metrics.revenueTrend
					},
					users: {
						total: metrics.totalClients,
						active: metrics.activeUsers
					},
					sessions: { active: metrics.activeUsers },
					packages: packages.data || [],
					locations: locations.data || [],
					churn: {
						rate: 5.2,
						atRisk: 12
					}
				};
			} catch (error) {
				console.error("Error fetching widget data:", error);
			}
		},
		addWidget(widget) {
			this.activeWidgets.push({ ...widget });
		},
		removeWidget(index) {
			this.activeWidgets.splice(index, 1);
		},
		moveWidget(index, direction) {
			const newIndex = direction === "up" ? index - 1 : index + 1;
			const widget = this.activeWidgets.splice(index, 1)[0];
			this.activeWidgets.splice(newIndex, 0, widget);
		},
		getWidgetClass(widget) {
			return widget.size === "Large" ? "md:col-span-2" : "";
		},
		getWidgetComponent(type) {
			return {
				revenue: {
					template: "<div><p class=\"text-xs text-slate-500 dark:text-slate-400 mb-1\">Total Revenue</p><p class=\"text-2xl font-bold text-slate-900 dark:text-white\">KES {{ data?.total || 0 }}</p><p class=\"text-xs text-emerald-600 mt-1\">↑ {{ data?.trend || \"up\" }}</p></div>",
					props: ["data"]
				},
				users: {
					template: "<div><p class=\"text-xs text-slate-500 dark:text-slate-400 mb-1\">Total Users</p><p class=\"text-2xl font-bold text-slate-900 dark:text-white\">{{ data?.total || 0 }}</p><p class=\"text-xs text-slate-600 dark:text-slate-400 mt-1\">{{ data?.active || 0 }} active</p></div>",
					props: ["data"]
				},
				sessions: {
					template: "<div><p class=\"text-xs text-slate-500 dark:text-slate-400 mb-1\">Active Sessions</p><p class=\"text-2xl font-bold text-slate-900 dark:text-white\">{{ data?.active || 0 }}</p></div>",
					props: ["data"]
				},
				packages: {
					template: "<div><p class=\"text-xs text-slate-500 dark:text-slate-400 mb-2\">Top Packages</p><div class=\"space-y-1\"><div v-for=\"pkg in (data || []).slice(0,3)\" :key=\"pkg.package__name\" class=\"text-xs\"><span class=\"font-medium text-slate-900 dark:text-white\">{{ pkg.package__name }}</span><span class=\"text-slate-500 ml-2\">{{ pkg.count }}</span></div></div></div>",
					props: ["data"]
				},
				locations: {
					template: "<div><p class=\"text-xs text-slate-500 dark:text-slate-400 mb-2\">Top Locations</p><div class=\"space-y-1\"><div v-for=\"loc in (data || []).slice(0,3)\" :key=\"loc.location__name\" class=\"text-xs\"><span class=\"font-medium text-slate-900 dark:text-white\">{{ loc.location__name }}</span><span class=\"text-slate-500 ml-2\">{{ loc.sales }}</span></div></div></div>",
					props: ["data"]
				},
				churn: {
					template: "<div><p class=\"text-xs text-slate-500 dark:text-slate-400 mb-1\">Churn Rate</p><p class=\"text-2xl font-bold text-red-600 dark:text-red-400\">{{ data?.rate || 0 }}%</p><p class=\"text-xs text-slate-600 dark:text-slate-400 mt-1\">{{ data?.atRisk || 0 }} at risk</p></div>",
					props: ["data"]
				}
			}[type] || { template: "<div>Widget</div>" };
		},
		saveLayout() {
			const name = prompt("Enter layout name:");
			if (name) {
				this.savedLayouts.push({
					name,
					widgets: [...this.activeWidgets],
					createdAt: (/* @__PURE__ */ new Date()).toISOString()
				});
				localStorage.setItem("dashboardLayouts", JSON.stringify(this.savedLayouts));
				alert("Layout saved!");
			}
		},
		loadLayout(layout) {
			this.activeWidgets = [...layout.widgets];
			this.showTemplates = false;
		},
		deleteLayout(index) {
			if (confirm("Delete this layout?")) {
				this.savedLayouts.splice(index, 1);
				localStorage.setItem("dashboardLayouts", JSON.stringify(this.savedLayouts));
			}
		},
		resetLayout() {
			if (confirm("Clear all widgets?")) this.activeWidgets = [];
		},
		applyTemplate(template) {
			this.activeWidgets = template.widgets.map((name) => this.availableWidgets.find((w) => w.name === name)).filter(Boolean);
			this.showTemplates = false;
		},
		loadSavedLayouts() {
			const saved = localStorage.getItem("dashboardLayouts");
			if (saved) this.savedLayouts = JSON.parse(saved);
		},
		formatDate(date) {
			return new Date(date).toLocaleDateString("en-US", {
				month: "short",
				day: "numeric"
			});
		}
	}
};
var _hoisted_1$28 = { class: "space-y-6" };
var _hoisted_2$28 = { class: "flex items-center justify-between" };
var _hoisted_3$28 = { class: "flex items-center gap-3" };
var _hoisted_4$28 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6" };
var _hoisted_5$28 = { class: "grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3" };
var _hoisted_6$28 = ["onClick"];
var _hoisted_7$28 = ["innerHTML"];
var _hoisted_8$28 = { class: "text-xs font-medium text-slate-900 dark:text-white" };
var _hoisted_9$26 = { class: "text-xs text-slate-500 dark:text-slate-400 mt-1" };
var _hoisted_10$24 = { class: "bg-slate-50 dark:bg-slate-900 rounded-xl border-2 border-dashed border-slate-300 dark:border-slate-700 p-6 min-h-[500px]" };
var _hoisted_11$23 = {
	key: 0,
	class: "flex flex-col items-center justify-center h-96"
};
var _hoisted_12$23 = {
	key: 1,
	class: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
};
var _hoisted_13$23 = { class: "absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity" };
var _hoisted_14$23 = ["onClick"];
var _hoisted_15$23 = ["onClick"];
var _hoisted_16$23 = ["onClick"];
var _hoisted_17$23 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6" };
var _hoisted_18$23 = { class: "grid grid-cols-1 md:grid-cols-3 gap-4" };
var _hoisted_19$21 = { class: "flex items-start justify-between mb-3" };
var _hoisted_20$21 = { class: "font-medium text-slate-900 dark:text-white" };
var _hoisted_21$21 = { class: "text-xs text-slate-500 dark:text-slate-400 mt-1" };
var _hoisted_22$21 = { class: "px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded" };
var _hoisted_23$21 = { class: "flex gap-2" };
var _hoisted_24$21 = ["onClick"];
var _hoisted_25$21 = ["onClick"];
var _hoisted_26$21 = {
	key: 0,
	class: "col-span-full text-center py-8 text-slate-400"
};
var _hoisted_27$20 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden" };
var _hoisted_28$20 = { class: "flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700" };
var _hoisted_29$20 = { class: "p-6 overflow-y-auto max-h-[calc(90vh-140px)]" };
var _hoisted_30$20 = { class: "grid grid-cols-1 md:grid-cols-2 gap-4" };
var _hoisted_31$19 = ["onClick"];
var _hoisted_32$18 = { class: "font-semibold text-slate-900 dark:text-white mb-2" };
var _hoisted_33$18 = { class: "text-sm text-slate-600 dark:text-slate-400 mb-3" };
var _hoisted_34$18 = { class: "flex flex-wrap gap-1" };
function _sfc_render$28(_ctx, _cache, $props, $setup, $data, $options) {
	return openBlock(), createElementBlock("div", _hoisted_1$28, [
		createBaseVNode("div", _hoisted_2$28, [_cache[7] || (_cache[7] = createBaseVNode("div", null, [createBaseVNode("h2", { class: "text-2xl font-bold text-slate-900 dark:text-white" }, "Custom Dashboard Builder"), createBaseVNode("p", { class: "text-sm text-slate-600 dark:text-slate-400 mt-1" }, "Create your personalized analytics dashboard")], -1)), createBaseVNode("div", _hoisted_3$28, [
			createBaseVNode("button", {
				onClick: _cache[0] || (_cache[0] = ($event) => $data.showTemplates = true),
				class: "px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm transition-colors flex items-center gap-2"
			}, [..._cache[5] || (_cache[5] = [createBaseVNode("svg", {
				class: "w-4 h-4",
				fill: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", { d: "M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z" })], -1), createTextVNode(" Templates ", -1)])]),
			createBaseVNode("button", {
				onClick: _cache[1] || (_cache[1] = (...args) => $options.resetLayout && $options.resetLayout(...args)),
				class: "px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg text-sm transition-colors"
			}, " Reset "),
			createBaseVNode("button", {
				onClick: _cache[2] || (_cache[2] = (...args) => $options.saveLayout && $options.saveLayout(...args)),
				class: "px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm transition-colors flex items-center gap-2"
			}, [..._cache[6] || (_cache[6] = [createBaseVNode("svg", {
				class: "w-4 h-4",
				fill: "none",
				stroke: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"
			})], -1), createTextVNode(" Save Layout ", -1)])])
		])]),
		createBaseVNode("div", _hoisted_4$28, [_cache[8] || (_cache[8] = createBaseVNode("h3", { class: "text-lg font-semibold text-slate-900 dark:text-white mb-4" }, "Widget Library", -1)), createBaseVNode("div", _hoisted_5$28, [(openBlock(true), createElementBlock(Fragment, null, renderList($data.availableWidgets, (widget) => {
			return openBlock(), createElementBlock("button", {
				key: widget.id,
				onClick: ($event) => $options.addWidget(widget),
				class: "p-4 rounded-lg border-2 border-slate-200 dark:border-slate-700 hover:border-blue-500 dark:hover:border-blue-500 hover:shadow-lg transition-all text-center group"
			}, [
				createBaseVNode("div", { class: normalizeClass(["w-12 h-12 mx-auto mb-2 rounded-lg flex items-center justify-center", widget.color]) }, [createBaseVNode("div", { innerHTML: widget.icon }, null, 8, _hoisted_7$28)], 2),
				createBaseVNode("p", _hoisted_8$28, toDisplayString(widget.name), 1),
				createBaseVNode("p", _hoisted_9$26, toDisplayString(widget.size), 1)
			], 8, _hoisted_6$28);
		}), 128))])]),
		createBaseVNode("div", _hoisted_10$24, [$data.activeWidgets.length === 0 ? (openBlock(), createElementBlock("div", _hoisted_11$23, [..._cache[9] || (_cache[9] = [
			createBaseVNode("svg", {
				class: "w-20 h-20 text-slate-300 dark:text-slate-600 mb-4",
				fill: "none",
				stroke: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
			})], -1),
			createBaseVNode("p", { class: "text-lg font-medium text-slate-600 dark:text-slate-400" }, "Your dashboard is empty", -1),
			createBaseVNode("p", { class: "text-sm text-slate-500 dark:text-slate-500 mt-2" }, "Click widgets above to add them to your dashboard", -1)
		])])) : (openBlock(), createElementBlock("div", _hoisted_12$23, [(openBlock(true), createElementBlock(Fragment, null, renderList($data.activeWidgets, (widget, index) => {
			return openBlock(), createElementBlock("div", {
				key: index,
				class: normalizeClass([$options.getWidgetClass(widget), "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 relative group shadow-sm hover:shadow-md transition-shadow"])
			}, [createBaseVNode("div", _hoisted_13$23, [
				index > 0 ? (openBlock(), createElementBlock("button", {
					key: 0,
					onClick: ($event) => $options.moveWidget(index, "up"),
					class: "p-1 bg-blue-500 hover:bg-blue-600 text-white rounded",
					title: "Move Up"
				}, [..._cache[10] || (_cache[10] = [createBaseVNode("svg", {
					class: "w-3 h-3",
					fill: "none",
					stroke: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", {
					"stroke-linecap": "round",
					"stroke-linejoin": "round",
					"stroke-width": "2",
					d: "M5 15l7-7 7 7"
				})], -1)])], 8, _hoisted_14$23)) : createCommentVNode("", true),
				index < $data.activeWidgets.length - 1 ? (openBlock(), createElementBlock("button", {
					key: 1,
					onClick: ($event) => $options.moveWidget(index, "down"),
					class: "p-1 bg-blue-500 hover:bg-blue-600 text-white rounded",
					title: "Move Down"
				}, [..._cache[11] || (_cache[11] = [createBaseVNode("svg", {
					class: "w-3 h-3",
					fill: "none",
					stroke: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", {
					"stroke-linecap": "round",
					"stroke-linejoin": "round",
					"stroke-width": "2",
					d: "M19 9l-7 7-7-7"
				})], -1)])], 8, _hoisted_15$23)) : createCommentVNode("", true),
				createBaseVNode("button", {
					onClick: ($event) => $options.removeWidget(index),
					class: "p-1 bg-red-500 hover:bg-red-600 text-white rounded",
					title: "Remove"
				}, [..._cache[12] || (_cache[12] = [createBaseVNode("svg", {
					class: "w-3 h-3",
					fill: "none",
					stroke: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", {
					"stroke-linecap": "round",
					"stroke-linejoin": "round",
					"stroke-width": "2",
					d: "M6 18L18 6M6 6l12 12"
				})], -1)])], 8, _hoisted_16$23)
			]), (openBlock(), createBlock(resolveDynamicComponent($options.getWidgetComponent(widget.type)), { data: $data.widgetData[widget.type] }, null, 8, ["data"]))], 2);
		}), 128))]))]),
		createBaseVNode("div", _hoisted_17$23, [_cache[13] || (_cache[13] = createBaseVNode("h3", { class: "text-lg font-semibold text-slate-900 dark:text-white mb-4" }, "Saved Layouts", -1)), createBaseVNode("div", _hoisted_18$23, [(openBlock(true), createElementBlock(Fragment, null, renderList($data.savedLayouts, (layout, index) => {
			return openBlock(), createElementBlock("div", {
				key: index,
				class: "p-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg border border-slate-200 dark:border-slate-600"
			}, [createBaseVNode("div", _hoisted_19$21, [createBaseVNode("div", null, [createBaseVNode("p", _hoisted_20$21, toDisplayString(layout.name), 1), createBaseVNode("p", _hoisted_21$21, toDisplayString(layout.widgets.length) + " widgets", 1)]), createBaseVNode("span", _hoisted_22$21, toDisplayString($options.formatDate(layout.createdAt)), 1)]), createBaseVNode("div", _hoisted_23$21, [createBaseVNode("button", {
				onClick: ($event) => $options.loadLayout(layout),
				class: "flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors"
			}, " Load ", 8, _hoisted_24$21), createBaseVNode("button", {
				onClick: ($event) => $options.deleteLayout(index),
				class: "px-3 py-2 bg-red-600 hover:bg-red-700 text-white text-sm rounded-lg transition-colors"
			}, " Delete ", 8, _hoisted_25$21)])]);
		}), 128)), $data.savedLayouts.length === 0 ? (openBlock(), createElementBlock("div", _hoisted_26$21, " No saved layouts yet ")) : createCommentVNode("", true)])]),
		$data.showTemplates ? (openBlock(), createElementBlock("div", {
			key: 0,
			class: "fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4",
			onClick: _cache[4] || (_cache[4] = withModifiers(($event) => $data.showTemplates = false, ["self"]))
		}, [createBaseVNode("div", _hoisted_27$20, [createBaseVNode("div", _hoisted_28$20, [_cache[15] || (_cache[15] = createBaseVNode("h2", { class: "text-lg font-semibold text-slate-900 dark:text-white" }, "Dashboard Templates", -1)), createBaseVNode("button", {
			onClick: _cache[3] || (_cache[3] = ($event) => $data.showTemplates = false),
			class: "p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg"
		}, [..._cache[14] || (_cache[14] = [createBaseVNode("svg", {
			class: "w-5 h-5",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M6 18L18 6M6 6l12 12"
		})], -1)])])]), createBaseVNode("div", _hoisted_29$20, [createBaseVNode("div", _hoisted_30$20, [(openBlock(true), createElementBlock(Fragment, null, renderList($data.templates, (template) => {
			return openBlock(), createElementBlock("button", {
				key: template.id,
				onClick: ($event) => $options.applyTemplate(template),
				class: "p-4 border-2 border-slate-200 dark:border-slate-700 hover:border-blue-500 dark:hover:border-blue-500 rounded-lg text-left transition-colors"
			}, [
				createBaseVNode("p", _hoisted_32$18, toDisplayString(template.name), 1),
				createBaseVNode("p", _hoisted_33$18, toDisplayString(template.description), 1),
				createBaseVNode("div", _hoisted_34$18, [(openBlock(true), createElementBlock(Fragment, null, renderList(template.widgets, (widget) => {
					return openBlock(), createElementBlock("span", {
						key: widget,
						class: "px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded"
					}, toDisplayString(widget), 1);
				}), 128))])
			], 8, _hoisted_31$19);
		}), 128))])])])])) : createCommentVNode("", true)
	]);
}
var DashboardBuilder_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$28, [["render", _sfc_render$28]]);
var _sfc_main$27 = {
	name: "ABTesting",
	props: {
		data: {
			type: Object,
			default: () => ({ experiments: [] })
		},
		loading: {
			type: Boolean,
			default: false
		}
	},
	emits: ["refresh"],
	data() {
		return {
			showModal: false,
			saveLoading: false,
			packages: [],
			formData: {
				name: "",
				package_id: "",
				promotion_type: "discount",
				discount_percentage: 10,
				priority: 1,
				start_date: (/* @__PURE__ */ new Date()).toISOString().split("T")[0],
				end_date: new Date(Date.now() + 720 * 60 * 60 * 1e3).toISOString().split("T")[0],
				is_active: true
			}
		};
	},
	mounted() {
		this.fetchPackages();
	},
	methods: {
		async fetchPackages() {
			try {
				const response = await fetch("https://srv.teralinkxwaves.uk/suapi/packages/", { headers: { "Authorization": `Bearer ${localStorage.getItem("access_token")}` } });
				if (response.ok) {
					const data = await response.json();
					this.packages = data.results || data;
				}
			} catch (error) {
				console.error("Error fetching packages:", error);
			}
		},
		closeModal() {
			this.showModal = false;
			this.formData = {
				name: "",
				package_id: "",
				promotion_type: "discount",
				discount_percentage: 10,
				priority: 1,
				start_date: (/* @__PURE__ */ new Date()).toISOString().split("T")[0],
				end_date: new Date(Date.now() + 720 * 60 * 60 * 1e3).toISOString().split("T")[0],
				is_active: true
			};
		},
		async createExperiment() {
			if (!this.formData.name || !this.formData.package_id) {
				alert("Please fill in all required fields");
				return;
			}
			this.saveLoading = true;
			try {
				const response = await fetch("https://srv.teralinkxwaves.uk/suapi/promotions/", {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
						"Authorization": `Bearer ${localStorage.getItem("access_token")}`
					},
					body: JSON.stringify(this.formData)
				});
				if (response.ok) {
					this.$emit("refresh");
					this.closeModal();
				} else {
					const error = await response.json();
					alert("Error: " + (error.message || "Failed to create experiment"));
				}
			} catch (error) {
				console.error("Error creating experiment:", error);
				alert("Failed to create experiment");
			} finally {
				this.saveLoading = false;
			}
		},
		getStatusBadge(status) {
			return {
				"running": "bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400",
				"completed": "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400",
				"ended": "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400",
				"paused": "bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400",
				"draft": "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400",
				"scheduled": "bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400"
			}[status] || "bg-slate-100 dark:bg-slate-700";
		},
		formatNumber(num) {
			return new Intl.NumberFormat().format(num);
		}
	}
};
var _hoisted_1$27 = { class: "space-y-4" };
var _hoisted_2$27 = { class: "flex items-center justify-between" };
var _hoisted_3$27 = {
	key: 0,
	class: "text-center py-8 text-slate-400"
};
var _hoisted_4$27 = {
	key: 1,
	class: "space-y-4"
};
var _hoisted_5$27 = { class: "flex items-center justify-between mb-4" };
var _hoisted_6$27 = { class: "text-sm font-medium text-slate-900 dark:text-white" };
var _hoisted_7$27 = { class: "text-xs text-slate-500 dark:text-slate-400 mt-1" };
var _hoisted_8$27 = { class: "grid grid-cols-1 md:grid-cols-2 gap-4 mb-4" };
var _hoisted_9$25 = { class: "flex items-center justify-between mb-2" };
var _hoisted_10$23 = { class: "text-sm font-medium text-slate-900 dark:text-white" };
var _hoisted_11$22 = {
	key: 0,
	class: "w-5 h-5 text-emerald-500",
	fill: "currentColor",
	viewBox: "0 0 24 24"
};
var _hoisted_12$22 = { class: "space-y-2" };
var _hoisted_13$22 = { class: "flex justify-between text-xs" };
var _hoisted_14$22 = { class: "font-semibold text-slate-900 dark:text-white" };
var _hoisted_15$22 = { class: "flex justify-between text-xs" };
var _hoisted_16$22 = { class: "font-semibold text-slate-900 dark:text-white" };
var _hoisted_17$22 = { class: "flex justify-between text-xs" };
var _hoisted_18$22 = { class: "font-bold text-blue-600 dark:text-blue-400" };
var _hoisted_19$20 = { class: "flex justify-between text-xs" };
var _hoisted_20$20 = { class: "font-semibold text-emerald-600 dark:text-emerald-400" };
var _hoisted_21$20 = { class: "flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg" };
var _hoisted_22$20 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full" };
var _hoisted_23$20 = { class: "flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700" };
var _hoisted_24$20 = { class: "p-6 space-y-4" };
var _hoisted_25$20 = { class: "grid grid-cols-2 gap-4" };
var _hoisted_26$20 = ["value"];
var _hoisted_27$19 = { class: "grid grid-cols-2 gap-4" };
var _hoisted_28$19 = { class: "grid grid-cols-2 gap-4" };
var _hoisted_29$19 = { class: "flex items-center gap-2 cursor-pointer" };
var _hoisted_30$19 = { class: "flex items-center justify-end gap-3 p-6 border-t border-slate-200 dark:border-slate-700" };
var _hoisted_31$18 = ["disabled"];
function _sfc_render$27(_ctx, _cache, $props, $setup, $data, $options) {
	return openBlock(), createElementBlock("div", _hoisted_1$27, [
		createBaseVNode("div", _hoisted_2$27, [_cache[13] || (_cache[13] = createBaseVNode("h2", { class: "text-lg font-semibold text-slate-900 dark:text-white" }, "A/B Testing Experiments", -1)), createBaseVNode("button", {
			onClick: _cache[0] || (_cache[0] = ($event) => $data.showModal = true),
			class: "px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm rounded-lg transition-colors"
		}, " New Experiment ")]),
		$props.loading ? (openBlock(), createElementBlock("div", _hoisted_3$27, "Loading...")) : (openBlock(), createElementBlock("div", _hoisted_4$27, [(openBlock(true), createElementBlock(Fragment, null, renderList($props.data.experiments, (exp) => {
			return openBlock(), createElementBlock("div", {
				key: exp.id,
				class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5"
			}, [
				createBaseVNode("div", _hoisted_5$27, [createBaseVNode("div", null, [createBaseVNode("h3", _hoisted_6$27, toDisplayString(exp.name), 1), createBaseVNode("p", _hoisted_7$27, "Started: " + toDisplayString(exp.start_date), 1)]), createBaseVNode("span", { class: normalizeClass(["px-3 py-1 rounded-full text-xs font-medium", $options.getStatusBadge(exp.status)]) }, toDisplayString(exp.status), 3)]),
				createBaseVNode("div", _hoisted_8$27, [(openBlock(true), createElementBlock(Fragment, null, renderList(exp.variants, (variant) => {
					return openBlock(), createElementBlock("div", {
						key: variant.name,
						class: normalizeClass(["p-4 rounded-lg border-2", variant.name === exp.winner ? "border-emerald-500 bg-emerald-50 dark:bg-emerald-500/10" : "border-slate-200 dark:border-slate-700"])
					}, [createBaseVNode("div", _hoisted_9$25, [createBaseVNode("span", _hoisted_10$23, toDisplayString(variant.name), 1), variant.name === exp.winner ? (openBlock(), createElementBlock("svg", _hoisted_11$22, [..._cache[14] || (_cache[14] = [createBaseVNode("path", { d: "M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" }, null, -1)])])) : createCommentVNode("", true)]), createBaseVNode("div", _hoisted_12$22, [
						createBaseVNode("div", _hoisted_13$22, [_cache[15] || (_cache[15] = createBaseVNode("span", { class: "text-slate-600 dark:text-slate-400" }, "Participants", -1)), createBaseVNode("span", _hoisted_14$22, toDisplayString(variant.participants), 1)]),
						createBaseVNode("div", _hoisted_15$22, [_cache[16] || (_cache[16] = createBaseVNode("span", { class: "text-slate-600 dark:text-slate-400" }, "Conversions", -1)), createBaseVNode("span", _hoisted_16$22, toDisplayString(variant.conversions), 1)]),
						createBaseVNode("div", _hoisted_17$22, [_cache[17] || (_cache[17] = createBaseVNode("span", { class: "text-slate-600 dark:text-slate-400" }, "Conv. Rate", -1)), createBaseVNode("span", _hoisted_18$22, toDisplayString(variant.conversion_rate) + "%", 1)]),
						createBaseVNode("div", _hoisted_19$20, [_cache[18] || (_cache[18] = createBaseVNode("span", { class: "text-slate-600 dark:text-slate-400" }, "Revenue", -1)), createBaseVNode("span", _hoisted_20$20, "KSh " + toDisplayString($options.formatNumber(variant.revenue)), 1)])
					])], 2);
				}), 128))]),
				createBaseVNode("div", _hoisted_21$20, [_cache[19] || (_cache[19] = createBaseVNode("div", { class: "flex items-center gap-2" }, [createBaseVNode("svg", {
					class: "w-4 h-4 text-blue-500",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z" })]), createBaseVNode("span", { class: "text-xs text-slate-600 dark:text-slate-400" }, "Statistical Confidence")], -1)), createBaseVNode("span", { class: normalizeClass(["text-sm font-bold", exp.confidence >= 95 ? "text-emerald-600 dark:text-emerald-400" : "text-amber-600 dark:text-amber-400"]) }, toDisplayString(exp.confidence) + "% ", 3)])
			]);
		}), 128))])),
		$data.showModal ? (openBlock(), createElementBlock("div", {
			key: 2,
			class: "fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4",
			onClick: _cache[12] || (_cache[12] = withModifiers((...args) => $options.closeModal && $options.closeModal(...args), ["self"]))
		}, [createBaseVNode("div", _hoisted_22$20, [
			createBaseVNode("div", _hoisted_23$20, [_cache[21] || (_cache[21] = createBaseVNode("h2", { class: "text-lg font-semibold text-slate-900 dark:text-white" }, "Create New Experiment", -1)), createBaseVNode("button", {
				onClick: _cache[1] || (_cache[1] = (...args) => $options.closeModal && $options.closeModal(...args)),
				class: "p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
			}, [..._cache[20] || (_cache[20] = [createBaseVNode("svg", {
				class: "w-5 h-5",
				fill: "none",
				stroke: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M6 18L18 6M6 6l12 12"
			})], -1)])])]),
			createBaseVNode("div", _hoisted_24$20, [
				createBaseVNode("div", null, [_cache[22] || (_cache[22] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2" }, "Experiment Name *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => $data.formData.name = $event),
					type: "text",
					required: "",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white",
					placeholder: "e.g., Homepage Banner Test"
				}, null, 512), [[vModelText, $data.formData.name]])]),
				createBaseVNode("div", _hoisted_25$20, [createBaseVNode("div", null, [_cache[24] || (_cache[24] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2" }, "Package *", -1)), withDirectives(createBaseVNode("select", {
					"onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => $data.formData.package_id = $event),
					required: "",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, [_cache[23] || (_cache[23] = createBaseVNode("option", { value: "" }, "Select Package", -1)), (openBlock(true), createElementBlock(Fragment, null, renderList($data.packages, (pkg) => {
					return openBlock(), createElementBlock("option", {
						key: pkg.id,
						value: pkg.id
					}, toDisplayString(pkg.name), 9, _hoisted_26$20);
				}), 128))], 512), [[vModelSelect, $data.formData.package_id]])]), createBaseVNode("div", null, [_cache[26] || (_cache[26] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2" }, "Promotion Type *", -1)), withDirectives(createBaseVNode("select", {
					"onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => $data.formData.promotion_type = $event),
					required: "",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, [..._cache[25] || (_cache[25] = [
					createBaseVNode("option", { value: "discount" }, "Discount", -1),
					createBaseVNode("option", { value: "bonus_data" }, "Bonus Data", -1),
					createBaseVNode("option", { value: "extended_validity" }, "Extended Validity", -1),
					createBaseVNode("option", { value: "free_trial" }, "Free Trial", -1)
				])], 512), [[vModelSelect, $data.formData.promotion_type]])])]),
				createBaseVNode("div", _hoisted_27$19, [createBaseVNode("div", null, [_cache[27] || (_cache[27] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2" }, "Discount % *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => $data.formData.discount_percentage = $event),
					type: "number",
					min: "0",
					max: "100",
					required: "",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $data.formData.discount_percentage]])]), createBaseVNode("div", null, [_cache[28] || (_cache[28] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2" }, "Priority", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => $data.formData.priority = $event),
					type: "number",
					min: "0",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $data.formData.priority]])])]),
				createBaseVNode("div", _hoisted_28$19, [createBaseVNode("div", null, [_cache[29] || (_cache[29] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2" }, "Start Date *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => $data.formData.start_date = $event),
					type: "date",
					required: "",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $data.formData.start_date]])]), createBaseVNode("div", null, [_cache[30] || (_cache[30] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2" }, "End Date *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[8] || (_cache[8] = ($event) => $data.formData.end_date = $event),
					type: "date",
					required: "",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $data.formData.end_date]])])]),
				createBaseVNode("div", null, [createBaseVNode("label", _hoisted_29$19, [withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[9] || (_cache[9] = ($event) => $data.formData.is_active = $event),
					type: "checkbox",
					class: "w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded"
				}, null, 512), [[vModelCheckbox, $data.formData.is_active]]), _cache[31] || (_cache[31] = createBaseVNode("span", { class: "text-sm text-slate-700 dark:text-slate-300" }, "Active", -1))])])
			]),
			createBaseVNode("div", _hoisted_30$19, [createBaseVNode("button", {
				onClick: _cache[10] || (_cache[10] = (...args) => $options.closeModal && $options.closeModal(...args)),
				class: "px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg"
			}, "Cancel"), createBaseVNode("button", {
				onClick: _cache[11] || (_cache[11] = (...args) => $options.createExperiment && $options.createExperiment(...args)),
				disabled: $data.saveLoading,
				class: normalizeClass(["px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg", { "opacity-50": $data.saveLoading }])
			}, toDisplayString($data.saveLoading ? "Creating..." : "Create"), 11, _hoisted_31$18)])
		])])) : createCommentVNode("", true)
	]);
}
var ABTesting_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$27, [["render", _sfc_render$27]]);
var _sfc_main$26 = {
	name: "CustomerHealth",
	props: {
		data: {
			type: Object,
			default: () => ({
				health_scores: [],
				summary: {}
			})
		},
		loading: {
			type: Boolean,
			default: false
		}
	},
	computed: { topCustomers() {
		return this.data.health_scores?.slice(0, 10) || [];
	} },
	methods: {
		getRiskBorder(risk) {
			return {
				"low": "border-emerald-200 dark:border-emerald-500/20 bg-emerald-50/50 dark:bg-emerald-500/5",
				"medium": "border-blue-200 dark:border-blue-500/20 bg-blue-50/50 dark:bg-blue-500/5",
				"high": "border-amber-200 dark:border-amber-500/20 bg-amber-50/50 dark:bg-amber-500/5",
				"critical": "border-red-200 dark:border-red-500/20 bg-red-50/50 dark:bg-red-500/5"
			}[risk] || "border-slate-200 dark:border-slate-700";
		},
		getRiskBadge(risk) {
			return {
				"low": "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400",
				"medium": "bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400",
				"high": "bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400",
				"critical": "bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400"
			}[risk] || "bg-slate-100 dark:bg-slate-700";
		},
		getScoreColor(score) {
			if (score >= 75) return "text-emerald-600 dark:text-emerald-400";
			if (score >= 50) return "text-blue-600 dark:text-blue-400";
			if (score >= 25) return "text-amber-600 dark:text-amber-400";
			return "text-red-600 dark:text-red-400";
		},
		formatDate(date) {
			if (!date) return "Never";
			return new Date(date).toLocaleDateString();
		}
	}
};
var _hoisted_1$26 = { class: "space-y-4" };
var _hoisted_2$26 = { class: "flex items-center justify-between" };
var _hoisted_3$26 = { class: "text-right" };
var _hoisted_4$26 = { class: "text-2xl font-bold text-blue-600 dark:text-blue-400" };
var _hoisted_5$26 = { class: "grid grid-cols-2 md:grid-cols-4 gap-3" };
var _hoisted_6$26 = { class: "p-3 rounded-lg bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20" };
var _hoisted_7$26 = { class: "text-2xl font-bold text-emerald-700 dark:text-emerald-300" };
var _hoisted_8$26 = { class: "p-3 rounded-lg bg-blue-50 dark:bg-blue-500/10 border border-blue-200 dark:border-blue-500/20" };
var _hoisted_9$24 = { class: "text-2xl font-bold text-blue-700 dark:text-blue-300" };
var _hoisted_10$22 = { class: "p-3 rounded-lg bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20" };
var _hoisted_11$21 = { class: "text-2xl font-bold text-amber-700 dark:text-amber-300" };
var _hoisted_12$21 = { class: "p-3 rounded-lg bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20" };
var _hoisted_13$21 = { class: "text-2xl font-bold text-red-700 dark:text-red-300" };
var _hoisted_14$21 = {
	key: 0,
	class: "text-center py-8 text-slate-400"
};
var _hoisted_15$21 = {
	key: 1,
	class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5"
};
var _hoisted_16$21 = { class: "space-y-3" };
var _hoisted_17$21 = { class: "flex items-center justify-between mb-3" };
var _hoisted_18$21 = { class: "text-sm font-medium text-slate-900 dark:text-white" };
var _hoisted_19$19 = { class: "text-xs text-slate-500 dark:text-slate-400 mt-0.5" };
var _hoisted_20$19 = { class: "text-right" };
var _hoisted_21$19 = { class: "grid grid-cols-3 gap-2" };
var _hoisted_22$19 = { class: "flex items-center gap-2 mt-1" };
var _hoisted_23$19 = { class: "flex-1 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden" };
var _hoisted_24$19 = { class: "text-xs font-medium text-slate-900 dark:text-white" };
var _hoisted_25$19 = { class: "flex items-center gap-2 mt-1" };
var _hoisted_26$19 = { class: "flex-1 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden" };
var _hoisted_27$18 = { class: "text-xs font-medium text-slate-900 dark:text-white" };
var _hoisted_28$18 = { class: "flex items-center gap-2 mt-1" };
var _hoisted_29$18 = { class: "flex-1 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden" };
var _hoisted_30$18 = { class: "text-xs font-medium text-slate-900 dark:text-white" };
function _sfc_render$26(_ctx, _cache, $props, $setup, $data, $options) {
	return openBlock(), createElementBlock("div", _hoisted_1$26, [
		createBaseVNode("div", _hoisted_2$26, [_cache[1] || (_cache[1] = createBaseVNode("h2", { class: "text-lg font-semibold text-slate-900 dark:text-white" }, "Customer Health Scores", -1)), createBaseVNode("div", _hoisted_3$26, [_cache[0] || (_cache[0] = createBaseVNode("p", { class: "text-xs text-slate-600 dark:text-slate-400" }, "Avg Health Score", -1)), createBaseVNode("p", _hoisted_4$26, toDisplayString($props.data.summary?.avg_health_score || 0), 1)])]),
		createBaseVNode("div", _hoisted_5$26, [
			createBaseVNode("div", _hoisted_6$26, [_cache[2] || (_cache[2] = createBaseVNode("p", { class: "text-xs text-emerald-600 dark:text-emerald-400 mb-1" }, "Low Risk", -1)), createBaseVNode("p", _hoisted_7$26, toDisplayString($props.data.summary?.low_risk || 0), 1)]),
			createBaseVNode("div", _hoisted_8$26, [_cache[3] || (_cache[3] = createBaseVNode("p", { class: "text-xs text-blue-600 dark:text-blue-400 mb-1" }, "Medium Risk", -1)), createBaseVNode("p", _hoisted_9$24, toDisplayString($props.data.summary?.medium_risk || 0), 1)]),
			createBaseVNode("div", _hoisted_10$22, [_cache[4] || (_cache[4] = createBaseVNode("p", { class: "text-xs text-amber-600 dark:text-amber-400 mb-1" }, "High Risk", -1)), createBaseVNode("p", _hoisted_11$21, toDisplayString($props.data.summary?.high_risk || 0), 1)]),
			createBaseVNode("div", _hoisted_12$21, [_cache[5] || (_cache[5] = createBaseVNode("p", { class: "text-xs text-red-600 dark:text-red-400 mb-1" }, "Critical", -1)), createBaseVNode("p", _hoisted_13$21, toDisplayString($props.data.summary?.critical_risk || 0), 1)])
		]),
		$props.loading ? (openBlock(), createElementBlock("div", _hoisted_14$21, "Loading...")) : (openBlock(), createElementBlock("div", _hoisted_15$21, [_cache[9] || (_cache[9] = createBaseVNode("h3", { class: "text-sm font-medium text-slate-900 dark:text-white mb-4" }, "Customer Health Details", -1)), createBaseVNode("div", _hoisted_16$21, [(openBlock(true), createElementBlock(Fragment, null, renderList($options.topCustomers, (customer) => {
			return openBlock(), createElementBlock("div", {
				key: customer.user_id,
				class: normalizeClass(["p-4 rounded-lg border", $options.getRiskBorder(customer.risk_level)])
			}, [createBaseVNode("div", _hoisted_17$21, [createBaseVNode("div", null, [createBaseVNode("p", _hoisted_18$21, toDisplayString(customer.username), 1), createBaseVNode("p", _hoisted_19$19, "Last activity: " + toDisplayString($options.formatDate(customer.last_activity)), 1)]), createBaseVNode("div", _hoisted_20$19, [createBaseVNode("p", { class: normalizeClass(["text-2xl font-bold", $options.getScoreColor(customer.health_score)]) }, toDisplayString(customer.health_score), 3), createBaseVNode("span", { class: normalizeClass(["text-xs px-2 py-1 rounded-full", $options.getRiskBadge(customer.risk_level)]) }, toDisplayString(customer.risk_level), 3)])]), createBaseVNode("div", _hoisted_21$19, [
				createBaseVNode("div", null, [_cache[6] || (_cache[6] = createBaseVNode("p", { class: "text-xs text-slate-600 dark:text-slate-400" }, "Engagement", -1)), createBaseVNode("div", _hoisted_22$19, [createBaseVNode("div", _hoisted_23$19, [createBaseVNode("div", {
					class: "h-full bg-blue-500",
					style: normalizeStyle({ width: customer.engagement_score + "%" })
				}, null, 4)]), createBaseVNode("span", _hoisted_24$19, toDisplayString(customer.engagement_score), 1)])]),
				createBaseVNode("div", null, [_cache[7] || (_cache[7] = createBaseVNode("p", { class: "text-xs text-slate-600 dark:text-slate-400" }, "Usage", -1)), createBaseVNode("div", _hoisted_25$19, [createBaseVNode("div", _hoisted_26$19, [createBaseVNode("div", {
					class: "h-full bg-purple-500",
					style: normalizeStyle({ width: customer.usage_score + "%" })
				}, null, 4)]), createBaseVNode("span", _hoisted_27$18, toDisplayString(customer.usage_score), 1)])]),
				createBaseVNode("div", null, [_cache[8] || (_cache[8] = createBaseVNode("p", { class: "text-xs text-slate-600 dark:text-slate-400" }, "Payment", -1)), createBaseVNode("div", _hoisted_28$18, [createBaseVNode("div", _hoisted_29$18, [createBaseVNode("div", {
					class: "h-full bg-emerald-500",
					style: normalizeStyle({ width: customer.payment_score + "%" })
				}, null, 4)]), createBaseVNode("span", _hoisted_30$18, toDisplayString(customer.payment_score), 1)])])
			])], 2);
		}), 128))])]))
	]);
}
var CustomerHealth_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$26, [["render", _sfc_render$26]]);
var _sfc_main$25 = {
	name: "AuditLogs",
	props: {
		data: {
			type: Object,
			default: () => ({
				logs: [],
				summary: {}
			})
		},
		loading: {
			type: Boolean,
			default: false
		}
	},
	data() {
		return {
			searchQuery: "",
			filterAction: "",
			filterSeverity: "",
			selectedLog: null,
			currentPage: 1,
			pageSize: 20
		};
	},
	computed: {
		filteredLogs() {
			let logs = this.data.logs || [];
			if (this.searchQuery) {
				const query = this.searchQuery.toLowerCase();
				logs = logs.filter((log) => log.user.toLowerCase().includes(query) || log.action.toLowerCase().includes(query) || log.category.toLowerCase().includes(query) || log.description.toLowerCase().includes(query) || log.ip_address.includes(query));
			}
			if (this.filterAction) logs = logs.filter((log) => log.action === this.filterAction);
			if (this.filterSeverity) logs = logs.filter((log) => log.severity === this.filterSeverity);
			return logs;
		},
		paginatedLogs() {
			const start = (this.currentPage - 1) * this.pageSize;
			const end = start + this.pageSize;
			return this.filteredLogs.slice(start, end);
		},
		totalPages() {
			return Math.ceil(this.filteredLogs.length / this.pageSize);
		},
		activeUsers() {
			return new Set((this.data.logs || []).map((log) => log.user)).size;
		}
	},
	watch: {
		searchQuery() {
			this.currentPage = 1;
		},
		filterAction() {
			this.currentPage = 1;
		},
		filterSeverity() {
			this.currentPage = 1;
		}
	},
	methods: {
		clearFilters() {
			this.searchQuery = "";
			this.filterAction = "";
			this.filterSeverity = "";
			this.currentPage = 1;
		},
		showDetails(log) {
			this.selectedLog = log;
		},
		getActionColor(action) {
			return {
				"CREATE": "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400",
				"UPDATE": "bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400",
				"DELETE": "bg-red-100 dark:bg-red-500/20 text-red-600 dark:text-red-400",
				"LOGIN": "bg-purple-100 dark:bg-purple-500/20 text-purple-600 dark:text-purple-400",
				"LOGOUT": "bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400",
				"VIEW": "bg-cyan-100 dark:bg-cyan-500/20 text-cyan-600 dark:text-cyan-400"
			}[action] || "bg-slate-100 dark:bg-slate-700";
		},
		getActionIcon(action) {
			const icons = {
				"CREATE": "<path d=\"M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm5 11h-4v4h-2v-4H7v-2h4V7h2v4h4v2z\"/>",
				"UPDATE": "<path d=\"M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z\"/>",
				"DELETE": "<path d=\"M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z\"/>",
				"LOGIN": "<path d=\"M11 7L9.6 8.4l2.6 2.6H2v2h10.2l-2.6 2.6L11 17l5-5-5-5zm9 12h-8v2h8c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2h-8v2h8v14z\"/>",
				"LOGOUT": "<path d=\"M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5-5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z\"/>",
				"VIEW": "<path d=\"M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z\"/>"
			};
			return icons[action] || icons["VIEW"];
		},
		getSeverityBadge(severity) {
			const badges = {
				"info": "bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400",
				"warning": "bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400",
				"critical": "bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400"
			};
			return badges[severity] || badges["info"];
		},
		formatTime(timestamp) {
			const date = new Date(timestamp);
			const now = /* @__PURE__ */ new Date();
			const diff = Math.floor((now - date) / 1e3);
			if (diff < 60) return "Just now";
			if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
			if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
			return `${Math.floor(diff / 86400)}d ago`;
		},
		formatDate(timestamp) {
			return new Date(timestamp).toLocaleDateString("en-US", {
				month: "short",
				day: "numeric",
				hour: "2-digit",
				minute: "2-digit"
			});
		},
		formatFullDate(timestamp) {
			return new Date(timestamp).toLocaleString("en-US", {
				year: "numeric",
				month: "long",
				day: "numeric",
				hour: "2-digit",
				minute: "2-digit",
				second: "2-digit"
			});
		}
	}
};
var _hoisted_1$25 = { class: "space-y-4" };
var _hoisted_2$25 = { class: "grid grid-cols-1 md:grid-cols-4 gap-4" };
var _hoisted_3$25 = { class: "bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-4 text-white" };
var _hoisted_4$25 = { class: "flex items-center justify-between" };
var _hoisted_5$25 = { class: "text-2xl font-bold mt-1" };
var _hoisted_6$25 = { class: "bg-gradient-to-br from-red-500 to-red-600 rounded-xl p-4 text-white" };
var _hoisted_7$25 = { class: "flex items-center justify-between" };
var _hoisted_8$25 = { class: "text-2xl font-bold mt-1" };
var _hoisted_9$23 = { class: "bg-gradient-to-br from-amber-500 to-amber-600 rounded-xl p-4 text-white" };
var _hoisted_10$21 = { class: "flex items-center justify-between" };
var _hoisted_11$20 = { class: "text-2xl font-bold mt-1" };
var _hoisted_12$20 = { class: "bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl p-4 text-white" };
var _hoisted_13$20 = { class: "flex items-center justify-between" };
var _hoisted_14$20 = { class: "text-2xl font-bold mt-1" };
var _hoisted_15$20 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4" };
var _hoisted_16$20 = { class: "flex flex-col md:flex-row gap-3" };
var _hoisted_17$20 = { class: "flex-1" };
var _hoisted_18$20 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden" };
var _hoisted_19$18 = {
	key: 0,
	class: "text-center py-12 text-slate-400"
};
var _hoisted_20$18 = {
	key: 1,
	class: "text-center py-12 text-slate-400"
};
var _hoisted_21$18 = {
	key: 2,
	class: "overflow-x-auto"
};
var _hoisted_22$18 = { class: "w-full" };
var _hoisted_23$18 = { class: "divide-y divide-slate-200 dark:divide-slate-700" };
var _hoisted_24$18 = { class: "px-4 py-3 whitespace-nowrap" };
var _hoisted_25$18 = { class: "text-xs text-slate-900 dark:text-white font-medium" };
var _hoisted_26$18 = { class: "text-xs text-slate-500 dark:text-slate-400" };
var _hoisted_27$17 = { class: "px-4 py-3 whitespace-nowrap" };
var _hoisted_28$17 = { class: "flex items-center gap-2" };
var _hoisted_29$17 = { class: "w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold" };
var _hoisted_30$17 = { class: "text-sm font-medium text-slate-900 dark:text-white" };
var _hoisted_31$17 = { class: "px-4 py-3 whitespace-nowrap" };
var _hoisted_32$17 = { class: "flex items-center gap-2" };
var _hoisted_33$17 = ["innerHTML"];
var _hoisted_34$17 = { class: "text-sm text-slate-900 dark:text-white" };
var _hoisted_35$17 = { class: "px-4 py-3" };
var _hoisted_36$17 = { class: "text-sm text-slate-900 dark:text-white" };
var _hoisted_37$17 = { class: "text-xs text-slate-500 dark:text-slate-400" };
var _hoisted_38$17 = { class: "px-4 py-3 whitespace-nowrap" };
var _hoisted_39$17 = { class: "text-xs font-mono text-slate-600 dark:text-slate-400" };
var _hoisted_40$17 = { class: "px-4 py-3 whitespace-nowrap" };
var _hoisted_41$16 = {
	key: 0,
	class: "ml-1 px-2 py-1 text-xs font-medium rounded-full bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400"
};
var _hoisted_42$14 = { class: "px-4 py-3 whitespace-nowrap text-right" };
var _hoisted_43$13 = ["onClick"];
var _hoisted_44$13 = {
	key: 3,
	class: "px-4 py-3 border-t border-slate-200 dark:border-slate-700 flex items-center justify-between"
};
var _hoisted_45$10 = { class: "text-sm text-slate-600 dark:text-slate-400" };
var _hoisted_46$10 = { class: "flex gap-2" };
var _hoisted_47$9 = ["disabled"];
var _hoisted_48$6 = ["disabled"];
var _hoisted_49$6 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden" };
var _hoisted_50$6 = { class: "flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700" };
var _hoisted_51$6 = { class: "p-6 overflow-y-auto max-h-[calc(90vh-140px)] space-y-4" };
var _hoisted_52$5 = { class: "grid grid-cols-2 gap-4" };
var _hoisted_53$5 = { class: "text-sm text-slate-900 dark:text-white" };
var _hoisted_54$4 = { class: "text-sm text-slate-900 dark:text-white" };
var _hoisted_55$3 = { class: "text-sm text-slate-900 dark:text-white" };
var _hoisted_56$2 = { class: "text-sm text-slate-900 dark:text-white" };
var _hoisted_57$2 = { class: "text-sm font-mono text-slate-900 dark:text-white" };
var _hoisted_58$2 = { class: "text-sm text-slate-900 dark:text-white" };
var _hoisted_59$2 = {
	key: 0,
	class: "p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-500/30 rounded-lg"
};
var _hoisted_60$2 = { class: "flex items-center justify-end gap-3 p-6 border-t border-slate-200 dark:border-slate-700" };
function _sfc_render$25(_ctx, _cache, $props, $setup, $data, $options) {
	return openBlock(), createElementBlock("div", _hoisted_1$25, [
		createBaseVNode("div", _hoisted_2$25, [
			createBaseVNode("div", _hoisted_3$25, [createBaseVNode("div", _hoisted_4$25, [createBaseVNode("div", null, [_cache[9] || (_cache[9] = createBaseVNode("p", { class: "text-blue-100 text-xs font-medium" }, "Total Logs (24h)", -1)), createBaseVNode("p", _hoisted_5$25, toDisplayString($props.data.summary?.total_24h || 0), 1)]), _cache[10] || (_cache[10] = createBaseVNode("svg", {
				class: "w-10 h-10 text-blue-200",
				fill: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", { d: "M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm2 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" })], -1))])]),
			createBaseVNode("div", _hoisted_6$25, [createBaseVNode("div", _hoisted_7$25, [createBaseVNode("div", null, [_cache[11] || (_cache[11] = createBaseVNode("p", { class: "text-red-100 text-xs font-medium" }, "Critical Events", -1)), createBaseVNode("p", _hoisted_8$25, toDisplayString($props.data.summary?.critical_24h || 0), 1)]), _cache[12] || (_cache[12] = createBaseVNode("svg", {
				class: "w-10 h-10 text-red-200",
				fill: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" })], -1))])]),
			createBaseVNode("div", _hoisted_9$23, [createBaseVNode("div", _hoisted_10$21, [createBaseVNode("div", null, [_cache[13] || (_cache[13] = createBaseVNode("p", { class: "text-amber-100 text-xs font-medium" }, "Suspicious Activity", -1)), createBaseVNode("p", _hoisted_11$20, toDisplayString($props.data.summary?.suspicious_24h || 0), 1)]), _cache[14] || (_cache[14] = createBaseVNode("svg", {
				class: "w-10 h-10 text-amber-200",
				fill: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z" })], -1))])]),
			createBaseVNode("div", _hoisted_12$20, [createBaseVNode("div", _hoisted_13$20, [createBaseVNode("div", null, [_cache[15] || (_cache[15] = createBaseVNode("p", { class: "text-emerald-100 text-xs font-medium" }, "Active Users", -1)), createBaseVNode("p", _hoisted_14$20, toDisplayString($options.activeUsers), 1)]), _cache[16] || (_cache[16] = createBaseVNode("svg", {
				class: "w-10 h-10 text-emerald-200",
				fill: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", { d: "M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z" })], -1))])])
		]),
		createBaseVNode("div", _hoisted_15$20, [createBaseVNode("div", _hoisted_16$20, [
			createBaseVNode("div", _hoisted_17$20, [withDirectives(createBaseVNode("input", {
				"onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => $data.searchQuery = $event),
				type: "text",
				placeholder: "Search by user, action, resource, IP address...",
				class: "w-full px-4 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm"
			}, null, 512), [[vModelText, $data.searchQuery]])]),
			withDirectives(createBaseVNode("select", {
				"onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => $data.filterAction = $event),
				class: "px-4 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm"
			}, [..._cache[17] || (_cache[17] = [createStaticVNode("<option value=\"\">All Actions</option><option value=\"CREATE\">Create</option><option value=\"UPDATE\">Update</option><option value=\"DELETE\">Delete</option><option value=\"LOGIN\">Login</option><option value=\"LOGOUT\">Logout</option><option value=\"VIEW\">View</option>", 7)])], 512), [[vModelSelect, $data.filterAction]]),
			withDirectives(createBaseVNode("select", {
				"onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => $data.filterSeverity = $event),
				class: "px-4 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm"
			}, [..._cache[18] || (_cache[18] = [
				createBaseVNode("option", { value: "" }, "All Severity", -1),
				createBaseVNode("option", { value: "info" }, "Info", -1),
				createBaseVNode("option", { value: "warning" }, "Warning", -1),
				createBaseVNode("option", { value: "critical" }, "Critical", -1)
			])], 512), [[vModelSelect, $data.filterSeverity]]),
			createBaseVNode("button", {
				onClick: _cache[3] || (_cache[3] = (...args) => $options.clearFilters && $options.clearFilters(...args)),
				class: "px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg text-sm transition-colors"
			}, " Clear ")
		])]),
		createBaseVNode("div", _hoisted_18$20, [$props.loading ? (openBlock(), createElementBlock("div", _hoisted_19$18, [..._cache[19] || (_cache[19] = [createBaseVNode("svg", {
			class: "animate-spin h-8 w-8 mx-auto mb-2",
			fill: "none",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("circle", {
			class: "opacity-25",
			cx: "12",
			cy: "12",
			r: "10",
			stroke: "currentColor",
			"stroke-width": "4"
		}), createBaseVNode("path", {
			class: "opacity-75",
			fill: "currentColor",
			d: "M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
		})], -1), createTextVNode(" Loading audit logs... ", -1)])])) : $options.filteredLogs.length === 0 ? (openBlock(), createElementBlock("div", _hoisted_20$18, [..._cache[20] || (_cache[20] = [createBaseVNode("svg", {
			class: "w-12 h-12 mx-auto mb-2",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
		})], -1), createTextVNode(" No logs found ", -1)])])) : (openBlock(), createElementBlock("div", _hoisted_21$18, [createBaseVNode("table", _hoisted_22$18, [_cache[21] || (_cache[21] = createBaseVNode("thead", { class: "bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700" }, [createBaseVNode("tr", null, [
			createBaseVNode("th", { class: "px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase" }, "Time"),
			createBaseVNode("th", { class: "px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase" }, "User"),
			createBaseVNode("th", { class: "px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase" }, "Action"),
			createBaseVNode("th", { class: "px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase" }, "Resource"),
			createBaseVNode("th", { class: "px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase" }, "IP Address"),
			createBaseVNode("th", { class: "px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase" }, "Severity"),
			createBaseVNode("th", { class: "px-4 py-3 text-right text-xs font-medium text-slate-500 dark:text-slate-400 uppercase" }, "Actions")
		])], -1)), createBaseVNode("tbody", _hoisted_23$18, [(openBlock(true), createElementBlock(Fragment, null, renderList($options.paginatedLogs, (log) => {
			return openBlock(), createElementBlock("tr", {
				key: log.id,
				class: normalizeClass(["hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors", { "bg-red-50 dark:bg-red-900/10": log.is_suspicious }])
			}, [
				createBaseVNode("td", _hoisted_24$18, [createBaseVNode("div", _hoisted_25$18, toDisplayString($options.formatTime(log.timestamp)), 1), createBaseVNode("div", _hoisted_26$18, toDisplayString($options.formatDate(log.timestamp)), 1)]),
				createBaseVNode("td", _hoisted_27$17, [createBaseVNode("div", _hoisted_28$17, [createBaseVNode("div", _hoisted_29$17, toDisplayString(log.user.charAt(0).toUpperCase()), 1), createBaseVNode("span", _hoisted_30$17, toDisplayString(log.user), 1)])]),
				createBaseVNode("td", _hoisted_31$17, [createBaseVNode("div", _hoisted_32$17, [createBaseVNode("div", { class: normalizeClass(["w-8 h-8 rounded-lg flex items-center justify-center", $options.getActionColor(log.action)]) }, [(openBlock(), createElementBlock("svg", {
					class: "w-4 h-4",
					fill: "currentColor",
					viewBox: "0 0 24 24",
					innerHTML: $options.getActionIcon(log.action)
				}, null, 8, _hoisted_33$17))], 2), createBaseVNode("span", _hoisted_34$17, toDisplayString(log.action), 1)])]),
				createBaseVNode("td", _hoisted_35$17, [createBaseVNode("div", _hoisted_36$17, toDisplayString(log.category), 1), createBaseVNode("div", _hoisted_37$17, toDisplayString(log.description), 1)]),
				createBaseVNode("td", _hoisted_38$17, [createBaseVNode("span", _hoisted_39$17, toDisplayString(log.ip_address), 1)]),
				createBaseVNode("td", _hoisted_40$17, [createBaseVNode("span", { class: normalizeClass(["px-2 py-1 text-xs font-medium rounded-full", $options.getSeverityBadge(log.severity)]) }, toDisplayString(log.severity), 3), log.is_suspicious ? (openBlock(), createElementBlock("span", _hoisted_41$16, " ⚠️ Suspicious ")) : createCommentVNode("", true)]),
				createBaseVNode("td", _hoisted_42$14, [createBaseVNode("button", {
					onClick: ($event) => $options.showDetails(log),
					class: "px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white text-xs rounded-lg transition-colors"
				}, " Details ", 8, _hoisted_43$13)])
			], 2);
		}), 128))])])])), $options.filteredLogs.length > 0 ? (openBlock(), createElementBlock("div", _hoisted_44$13, [createBaseVNode("div", _hoisted_45$10, " Showing " + toDisplayString(($data.currentPage - 1) * $data.pageSize + 1) + " to " + toDisplayString(Math.min($data.currentPage * $data.pageSize, $options.filteredLogs.length)) + " of " + toDisplayString($options.filteredLogs.length) + " logs ", 1), createBaseVNode("div", _hoisted_46$10, [createBaseVNode("button", {
			onClick: _cache[4] || (_cache[4] = ($event) => $data.currentPage--),
			disabled: $data.currentPage === 1,
			class: "px-3 py-1 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
		}, " Previous ", 8, _hoisted_47$9), createBaseVNode("button", {
			onClick: _cache[5] || (_cache[5] = ($event) => $data.currentPage++),
			disabled: $data.currentPage >= $options.totalPages,
			class: "px-3 py-1 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
		}, " Next ", 8, _hoisted_48$6)])])) : createCommentVNode("", true)]),
		$data.selectedLog ? (openBlock(), createElementBlock("div", {
			key: 0,
			class: "fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4",
			onClick: _cache[8] || (_cache[8] = withModifiers(($event) => $data.selectedLog = null, ["self"]))
		}, [createBaseVNode("div", _hoisted_49$6, [
			createBaseVNode("div", _hoisted_50$6, [_cache[23] || (_cache[23] = createBaseVNode("h2", { class: "text-lg font-semibold text-slate-900 dark:text-white" }, "Audit Log Details", -1)), createBaseVNode("button", {
				onClick: _cache[6] || (_cache[6] = ($event) => $data.selectedLog = null),
				class: "p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
			}, [..._cache[22] || (_cache[22] = [createBaseVNode("svg", {
				class: "w-5 h-5",
				fill: "none",
				stroke: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M6 18L18 6M6 6l12 12"
			})], -1)])])]),
			createBaseVNode("div", _hoisted_51$6, [
				createBaseVNode("div", _hoisted_52$5, [
					createBaseVNode("div", null, [_cache[24] || (_cache[24] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1" }, "Timestamp", -1)), createBaseVNode("p", _hoisted_53$5, toDisplayString($options.formatFullDate($data.selectedLog.timestamp)), 1)]),
					createBaseVNode("div", null, [_cache[25] || (_cache[25] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1" }, "User", -1)), createBaseVNode("p", _hoisted_54$4, toDisplayString($data.selectedLog.user), 1)]),
					createBaseVNode("div", null, [_cache[26] || (_cache[26] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1" }, "Action", -1)), createBaseVNode("p", _hoisted_55$3, toDisplayString($data.selectedLog.action), 1)]),
					createBaseVNode("div", null, [_cache[27] || (_cache[27] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1" }, "Category", -1)), createBaseVNode("p", _hoisted_56$2, toDisplayString($data.selectedLog.category), 1)]),
					createBaseVNode("div", null, [_cache[28] || (_cache[28] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1" }, "IP Address", -1)), createBaseVNode("p", _hoisted_57$2, toDisplayString($data.selectedLog.ip_address), 1)]),
					createBaseVNode("div", null, [_cache[29] || (_cache[29] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1" }, "Severity", -1)), createBaseVNode("span", { class: normalizeClass(["px-2 py-1 text-xs font-medium rounded-full", $options.getSeverityBadge($data.selectedLog.severity)]) }, toDisplayString($data.selectedLog.severity), 3)])
				]),
				createBaseVNode("div", null, [_cache[30] || (_cache[30] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1" }, "Description", -1)), createBaseVNode("p", _hoisted_58$2, toDisplayString($data.selectedLog.description), 1)]),
				$data.selectedLog.is_suspicious ? (openBlock(), createElementBlock("div", _hoisted_59$2, [..._cache[31] || (_cache[31] = [createStaticVNode("<div class=\"flex items-center gap-2 mb-2\"><svg class=\"w-5 h-5 text-red-600 dark:text-red-400\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z\"></path></svg><span class=\"text-sm font-semibold text-red-900 dark:text-red-400\">Suspicious Activity Detected</span></div><p class=\"text-xs text-red-700 dark:text-red-300\">This activity has been flagged as potentially suspicious and requires review.</p>", 2)])])) : createCommentVNode("", true)
			]),
			createBaseVNode("div", _hoisted_60$2, [createBaseVNode("button", {
				onClick: _cache[7] || (_cache[7] = ($event) => $data.selectedLog = null),
				class: "px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg"
			}, "Close")])
		])])) : createCommentVNode("", true)
	]);
}
var AuditLogs_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$25, [["render", _sfc_render$25]]);
var _sfc_main$24 = {
	name: "DataQuality",
	props: {
		data: {
			type: Object,
			default: () => ({
				checks: [],
				overall_score: 0,
				total_issues: 0,
				last_check: null,
				trend: 0
			})
		},
		loading: {
			type: Boolean,
			default: false
		}
	},
	emits: ["refresh"],
	data() {
		return { selectedCheck: null };
	},
	computed: {
		passedChecks() {
			return (this.data.checks || []).filter((c) => c.status === "passed").length;
		},
		warningChecks() {
			return (this.data.checks || []).filter((c) => c.status === "warning").length;
		},
		failedChecks() {
			return (this.data.checks || []).filter((c) => c.status === "failed").length;
		},
		recommendations() {
			const recs = [];
			(this.data.checks || []).forEach((check) => {
				if (check.status === "failed" || check.status === "warning") recs.push({
					title: `Improve ${check.table} ${check.check}`,
					description: this.getRecommendation(check)
				});
			});
			return recs.slice(0, 5);
		}
	},
	methods: {
		runChecks() {
			this.$emit("refresh");
		},
		showDetails(check) {
			this.selectedCheck = check;
		},
		getCheckBorder(status) {
			return {
				"passed": "border-emerald-200 dark:border-emerald-500/20 bg-emerald-50/50 dark:bg-emerald-500/5",
				"warning": "border-amber-200 dark:border-amber-500/20 bg-amber-50/50 dark:bg-amber-500/5",
				"failed": "border-red-200 dark:border-red-500/20 bg-red-50/50 dark:bg-red-500/5"
			}[status] || "border-slate-200 dark:border-slate-700";
		},
		getStatusBadge(status) {
			return {
				"passed": "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400",
				"warning": "bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400",
				"failed": "bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400"
			}[status] || "bg-slate-100 dark:bg-slate-700";
		},
		getScoreColor(score) {
			if (score >= 95) return "text-emerald-600 dark:text-emerald-400";
			if (score >= 85) return "text-blue-600 dark:text-blue-400";
			if (score >= 70) return "text-amber-600 dark:text-amber-400";
			return "text-red-600 dark:text-red-400";
		},
		getScoreBar(score) {
			if (score >= 95) return "bg-emerald-500";
			if (score >= 85) return "bg-blue-500";
			if (score >= 70) return "bg-amber-500";
			return "bg-red-500";
		},
		getTrendIcon(trend) {
			if (trend > 0) return "text-emerald-300";
			if (trend < 0) return "text-red-300";
			return "text-cyan-300";
		},
		formatTime(timestamp) {
			if (!timestamp) return "Never";
			const date = new Date(timestamp);
			const now = /* @__PURE__ */ new Date();
			const diff = Math.floor((now - date) / 1e3);
			if (diff < 60) return "Just now";
			if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
			if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
			return date.toLocaleDateString();
		},
		getRecommendation(check) {
			return {
				"Completeness": `Review and fill in missing ${check.table} data. Implement validation rules to prevent incomplete records.`,
				"Accuracy": `Verify ${check.table} data accuracy. Cross-reference with source systems and correct discrepancies.`,
				"Consistency": `Standardize ${check.table} data formats. Implement data normalization procedures.`,
				"Timeliness": `Update ${check.table} records more frequently. Set up automated data refresh schedules.`,
				"Validity": `Validate ${check.table} data against business rules. Remove or correct invalid entries.`
			}[check.check] || `Review and improve ${check.table} data quality.`;
		}
	}
};
var _hoisted_1$24 = { class: "space-y-6" };
var _hoisted_2$24 = { class: "bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl p-6 text-white shadow-lg" };
var _hoisted_3$24 = { class: "flex items-center justify-between" };
var _hoisted_4$24 = { class: "flex items-baseline gap-3" };
var _hoisted_5$24 = { class: "text-5xl font-bold" };
var _hoisted_6$24 = { class: "text-cyan-100 text-xs mt-2" };
var _hoisted_7$24 = { class: "text-right" };
var _hoisted_8$24 = { class: "w-32 h-32 relative" };
var _hoisted_9$22 = {
	class: "transform -rotate-90",
	viewBox: "0 0 120 120"
};
var _hoisted_10$20 = ["stroke-dashoffset"];
var _hoisted_11$19 = { class: "grid grid-cols-2 md:grid-cols-4 gap-4" };
var _hoisted_12$19 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4" };
var _hoisted_13$19 = { class: "flex items-center gap-2 mb-2" };
var _hoisted_14$19 = { class: "text-xl font-bold text-slate-900 dark:text-white" };
var _hoisted_15$19 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4" };
var _hoisted_16$19 = { class: "flex items-center gap-2 mb-2" };
var _hoisted_17$19 = { class: "text-xl font-bold text-slate-900 dark:text-white" };
var _hoisted_18$19 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4" };
var _hoisted_19$17 = { class: "flex items-center gap-2 mb-2" };
var _hoisted_20$17 = { class: "text-xl font-bold text-slate-900 dark:text-white" };
var _hoisted_21$17 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4" };
var _hoisted_22$17 = { class: "flex items-center gap-2 mb-2" };
var _hoisted_23$17 = { class: "text-xl font-bold text-slate-900 dark:text-white" };
var _hoisted_24$17 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden" };
var _hoisted_25$17 = { class: "p-6 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center" };
var _hoisted_26$17 = ["disabled"];
var _hoisted_27$16 = {
	key: 0,
	class: "p-12 text-center"
};
var _hoisted_28$16 = {
	key: 1,
	class: "overflow-x-auto"
};
var _hoisted_29$16 = { class: "w-full" };
var _hoisted_30$16 = { class: "divide-y divide-slate-200 dark:divide-slate-700" };
var _hoisted_31$16 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_32$16 = { class: "flex items-center gap-2" };
var _hoisted_33$16 = { class: "text-sm font-medium text-slate-900 dark:text-white" };
var _hoisted_34$16 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_35$16 = { class: "text-sm text-slate-600 dark:text-slate-400" };
var _hoisted_36$16 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_37$16 = { class: "flex items-center gap-3" };
var _hoisted_38$16 = { class: "flex-1 w-24 h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden" };
var _hoisted_39$16 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_40$16 = { class: "text-sm font-semibold text-slate-900 dark:text-white" };
var _hoisted_41$15 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_42$13 = { class: "px-6 py-4 whitespace-nowrap text-right" };
var _hoisted_43$12 = ["onClick"];
var _hoisted_44$12 = {
	key: 0,
	class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6"
};
var _hoisted_45$9 = { class: "space-y-3" };
var _hoisted_46$9 = { class: "flex items-start gap-3" };
var _hoisted_47$8 = { class: "flex-1" };
var _hoisted_48$5 = { class: "text-sm font-medium text-slate-900 dark:text-white" };
var _hoisted_49$5 = { class: "text-xs text-slate-600 dark:text-slate-400 mt-1" };
var _hoisted_50$5 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full" };
var _hoisted_51$5 = { class: "flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700" };
var _hoisted_52$4 = { class: "p-6 space-y-4" };
var _hoisted_53$4 = { class: "grid grid-cols-2 gap-4" };
var _hoisted_54$3 = { class: "text-sm font-semibold text-slate-900 dark:text-white" };
var _hoisted_55$2 = { class: "text-sm font-semibold text-slate-900 dark:text-white" };
var _hoisted_56$1 = { class: "p-4 bg-slate-50 dark:bg-slate-900 rounded-lg" };
var _hoisted_57$1 = { class: "text-3xl font-bold text-slate-900 dark:text-white" };
var _hoisted_58$1 = { class: "p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-500/30 rounded-lg" };
var _hoisted_59$1 = { class: "text-xs text-blue-700 dark:text-blue-300" };
var _hoisted_60$1 = { class: "flex items-center justify-end gap-3 p-6 border-t border-slate-200 dark:border-slate-700" };
function _sfc_render$24(_ctx, _cache, $props, $setup, $data, $options) {
	return openBlock(), createElementBlock("div", _hoisted_1$24, [
		createBaseVNode("div", _hoisted_2$24, [createBaseVNode("div", _hoisted_3$24, [createBaseVNode("div", null, [
			_cache[4] || (_cache[4] = createBaseVNode("p", { class: "text-cyan-100 text-sm font-medium mb-2" }, "Overall Data Quality Score", -1)),
			createBaseVNode("div", _hoisted_4$24, [createBaseVNode("p", _hoisted_5$24, toDisplayString($props.data.overall_score || 0) + "%", 1), createBaseVNode("span", { class: normalizeClass(["text-lg", $options.getTrendIcon($props.data.trend)]) }, toDisplayString($props.data.trend > 0 ? "↑" : $props.data.trend < 0 ? "↓" : "→") + " " + toDisplayString(Math.abs($props.data.trend || 0)) + "% ", 3)]),
			createBaseVNode("p", _hoisted_6$24, "Last checked: " + toDisplayString($options.formatTime($props.data.last_check)), 1)
		]), createBaseVNode("div", _hoisted_7$24, [createBaseVNode("div", _hoisted_8$24, [(openBlock(), createElementBlock("svg", _hoisted_9$22, [_cache[5] || (_cache[5] = createBaseVNode("circle", {
			cx: "60",
			cy: "60",
			r: "54",
			fill: "none",
			stroke: "rgba(255,255,255,0.2)",
			"stroke-width": "12"
		}, null, -1)), createBaseVNode("circle", {
			cx: "60",
			cy: "60",
			r: "54",
			fill: "none",
			stroke: "white",
			"stroke-width": "12",
			"stroke-dasharray": "339.292",
			"stroke-dashoffset": 339.292 - 339.292 * ($props.data.overall_score || 0) / 100,
			"stroke-linecap": "round"
		}, null, 8, _hoisted_10$20)])), _cache[6] || (_cache[6] = createBaseVNode("div", { class: "absolute inset-0 flex items-center justify-center" }, [createBaseVNode("svg", {
			class: "w-12 h-12",
			fill: "white",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" })])], -1))])])])]),
		createBaseVNode("div", _hoisted_11$19, [
			createBaseVNode("div", _hoisted_12$19, [createBaseVNode("div", _hoisted_13$19, [_cache[8] || (_cache[8] = createBaseVNode("div", { class: "w-10 h-10 rounded-lg bg-emerald-100 dark:bg-emerald-500/20 flex items-center justify-center" }, [createBaseVNode("svg", {
				class: "w-5 h-5 text-emerald-600 dark:text-emerald-400",
				fill: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" })])], -1)), createBaseVNode("div", null, [_cache[7] || (_cache[7] = createBaseVNode("p", { class: "text-xs text-slate-600 dark:text-slate-400" }, "Passed", -1)), createBaseVNode("p", _hoisted_14$19, toDisplayString($options.passedChecks), 1)])])]),
			createBaseVNode("div", _hoisted_15$19, [createBaseVNode("div", _hoisted_16$19, [_cache[10] || (_cache[10] = createBaseVNode("div", { class: "w-10 h-10 rounded-lg bg-amber-100 dark:bg-amber-500/20 flex items-center justify-center" }, [createBaseVNode("svg", {
				class: "w-5 h-5 text-amber-600 dark:text-amber-400",
				fill: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", { d: "M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z" })])], -1)), createBaseVNode("div", null, [_cache[9] || (_cache[9] = createBaseVNode("p", { class: "text-xs text-slate-600 dark:text-slate-400" }, "Warnings", -1)), createBaseVNode("p", _hoisted_17$19, toDisplayString($options.warningChecks), 1)])])]),
			createBaseVNode("div", _hoisted_18$19, [createBaseVNode("div", _hoisted_19$17, [_cache[12] || (_cache[12] = createBaseVNode("div", { class: "w-10 h-10 rounded-lg bg-red-100 dark:bg-red-500/20 flex items-center justify-center" }, [createBaseVNode("svg", {
				class: "w-5 h-5 text-red-600 dark:text-red-400",
				fill: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" })])], -1)), createBaseVNode("div", null, [_cache[11] || (_cache[11] = createBaseVNode("p", { class: "text-xs text-slate-600 dark:text-slate-400" }, "Failed", -1)), createBaseVNode("p", _hoisted_20$17, toDisplayString($options.failedChecks), 1)])])]),
			createBaseVNode("div", _hoisted_21$17, [createBaseVNode("div", _hoisted_22$17, [_cache[14] || (_cache[14] = createBaseVNode("div", { class: "w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-500/20 flex items-center justify-center" }, [createBaseVNode("svg", {
				class: "w-5 h-5 text-blue-600 dark:text-blue-400",
				fill: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", { d: "M11 15h2v2h-2zm0-8h2v6h-2zm.99-5C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z" })])], -1)), createBaseVNode("div", null, [_cache[13] || (_cache[13] = createBaseVNode("p", { class: "text-xs text-slate-600 dark:text-slate-400" }, "Total Issues", -1)), createBaseVNode("p", _hoisted_23$17, toDisplayString($props.data.total_issues || 0), 1)])])])
		]),
		createBaseVNode("div", _hoisted_24$17, [createBaseVNode("div", _hoisted_25$17, [_cache[16] || (_cache[16] = createBaseVNode("h3", { class: "text-lg font-semibold text-slate-900 dark:text-white" }, "Data Quality Checks", -1)), createBaseVNode("button", {
			onClick: _cache[0] || (_cache[0] = (...args) => $options.runChecks && $options.runChecks(...args)),
			disabled: $props.loading,
			class: normalizeClass(["px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm transition-colors flex items-center gap-2", { "opacity-50": $props.loading }])
		}, [(openBlock(), createElementBlock("svg", {
			class: normalizeClass(["w-4 h-4", { "animate-spin": $props.loading }]),
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [..._cache[15] || (_cache[15] = [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
		}, null, -1)])], 2)), createTextVNode(" " + toDisplayString($props.loading ? "Running..." : "Run Checks"), 1)], 10, _hoisted_26$17)]), $props.loading ? (openBlock(), createElementBlock("div", _hoisted_27$16, [..._cache[17] || (_cache[17] = [createBaseVNode("svg", {
			class: "animate-spin h-10 w-10 mx-auto mb-4 text-blue-600",
			fill: "none",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("circle", {
			class: "opacity-25",
			cx: "12",
			cy: "12",
			r: "10",
			stroke: "currentColor",
			"stroke-width": "4"
		}), createBaseVNode("path", {
			class: "opacity-75",
			fill: "currentColor",
			d: "M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
		})], -1), createBaseVNode("p", { class: "text-slate-600 dark:text-slate-400" }, "Running quality checks...", -1)])])) : (openBlock(), createElementBlock("div", _hoisted_28$16, [createBaseVNode("table", _hoisted_29$16, [_cache[19] || (_cache[19] = createBaseVNode("thead", { class: "bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700" }, [createBaseVNode("tr", null, [
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase" }, "Table"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase" }, "Check Type"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase" }, "Score"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase" }, "Issues"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase" }, "Status"),
			createBaseVNode("th", { class: "px-6 py-3 text-right text-xs font-medium text-slate-500 dark:text-slate-400 uppercase" }, "Actions")
		])], -1)), createBaseVNode("tbody", _hoisted_30$16, [(openBlock(true), createElementBlock(Fragment, null, renderList($props.data.checks, (check) => {
			return openBlock(), createElementBlock("tr", {
				key: check.table + check.check,
				class: "hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors"
			}, [
				createBaseVNode("td", _hoisted_31$16, [createBaseVNode("div", _hoisted_32$16, [_cache[18] || (_cache[18] = createBaseVNode("svg", {
					class: "w-5 h-5 text-slate-400",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-1 9H9V9h10v2zm-4 4H9v-2h6v2zm4-8H9V5h10v2z" })], -1)), createBaseVNode("span", _hoisted_33$16, toDisplayString(check.table), 1)])]),
				createBaseVNode("td", _hoisted_34$16, [createBaseVNode("span", _hoisted_35$16, toDisplayString(check.check), 1)]),
				createBaseVNode("td", _hoisted_36$16, [createBaseVNode("div", _hoisted_37$16, [createBaseVNode("div", _hoisted_38$16, [createBaseVNode("div", {
					class: normalizeClass(["h-full transition-all", $options.getScoreBar(check.score)]),
					style: normalizeStyle({ width: check.score + "%" })
				}, null, 6)]), createBaseVNode("span", { class: normalizeClass(["text-sm font-bold", $options.getScoreColor(check.score)]) }, toDisplayString(check.score) + "%", 3)])]),
				createBaseVNode("td", _hoisted_39$16, [createBaseVNode("span", _hoisted_40$16, toDisplayString(check.issues), 1)]),
				createBaseVNode("td", _hoisted_41$15, [createBaseVNode("span", { class: normalizeClass(["px-3 py-1 text-xs font-medium rounded-full", $options.getStatusBadge(check.status)]) }, toDisplayString(check.status), 3)]),
				createBaseVNode("td", _hoisted_42$13, [createBaseVNode("button", {
					onClick: ($event) => $options.showDetails(check),
					class: "px-3 py-1 bg-blue-500 hover:bg-blue-600 text-white text-xs rounded-lg transition-colors"
				}, " View Details ", 8, _hoisted_43$12)])
			]);
		}), 128))])])]))]),
		$options.recommendations.length > 0 ? (openBlock(), createElementBlock("div", _hoisted_44$12, [_cache[21] || (_cache[21] = createBaseVNode("h3", { class: "text-lg font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2" }, [createBaseVNode("svg", {
			class: "w-5 h-5 text-amber-500",
			fill: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", { d: "M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" })]), createTextVNode(" Recommendations ")], -1)), createBaseVNode("div", _hoisted_45$9, [(openBlock(true), createElementBlock(Fragment, null, renderList($options.recommendations, (rec, index) => {
			return openBlock(), createElementBlock("div", {
				key: index,
				class: "p-4 bg-amber-50 dark:bg-amber-900/10 border border-amber-200 dark:border-amber-500/20 rounded-lg"
			}, [createBaseVNode("div", _hoisted_46$9, [_cache[20] || (_cache[20] = createBaseVNode("svg", {
				class: "w-5 h-5 text-amber-600 dark:text-amber-400 mt-0.5",
				fill: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z" })], -1)), createBaseVNode("div", _hoisted_47$8, [createBaseVNode("p", _hoisted_48$5, toDisplayString(rec.title), 1), createBaseVNode("p", _hoisted_49$5, toDisplayString(rec.description), 1)])])]);
		}), 128))])])) : createCommentVNode("", true),
		$data.selectedCheck ? (openBlock(), createElementBlock("div", {
			key: 1,
			class: "fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4",
			onClick: _cache[3] || (_cache[3] = withModifiers(($event) => $data.selectedCheck = null, ["self"]))
		}, [createBaseVNode("div", _hoisted_50$5, [
			createBaseVNode("div", _hoisted_51$5, [_cache[23] || (_cache[23] = createBaseVNode("h2", { class: "text-lg font-semibold text-slate-900 dark:text-white" }, "Quality Check Details", -1)), createBaseVNode("button", {
				onClick: _cache[1] || (_cache[1] = ($event) => $data.selectedCheck = null),
				class: "p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
			}, [..._cache[22] || (_cache[22] = [createBaseVNode("svg", {
				class: "w-5 h-5",
				fill: "none",
				stroke: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M6 18L18 6M6 6l12 12"
			})], -1)])])]),
			createBaseVNode("div", _hoisted_52$4, [
				createBaseVNode("div", _hoisted_53$4, [
					createBaseVNode("div", null, [_cache[24] || (_cache[24] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1" }, "Table", -1)), createBaseVNode("p", _hoisted_54$3, toDisplayString($data.selectedCheck.table), 1)]),
					createBaseVNode("div", null, [_cache[25] || (_cache[25] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1" }, "Check Type", -1)), createBaseVNode("p", _hoisted_55$2, toDisplayString($data.selectedCheck.check), 1)]),
					createBaseVNode("div", null, [_cache[26] || (_cache[26] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1" }, "Score", -1)), createBaseVNode("p", { class: normalizeClass(["text-2xl font-bold", $options.getScoreColor($data.selectedCheck.score)]) }, toDisplayString($data.selectedCheck.score) + "%", 3)]),
					createBaseVNode("div", null, [_cache[27] || (_cache[27] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1" }, "Status", -1)), createBaseVNode("span", { class: normalizeClass(["px-3 py-1 text-xs font-medium rounded-full", $options.getStatusBadge($data.selectedCheck.status)]) }, toDisplayString($data.selectedCheck.status), 3)])
				]),
				createBaseVNode("div", null, [_cache[29] || (_cache[29] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-500 dark:text-slate-400 mb-2" }, "Issues Found", -1)), createBaseVNode("div", _hoisted_56$1, [createBaseVNode("p", _hoisted_57$1, toDisplayString($data.selectedCheck.issues), 1), _cache[28] || (_cache[28] = createBaseVNode("p", { class: "text-xs text-slate-600 dark:text-slate-400 mt-1" }, "records with data quality issues", -1))])]),
				createBaseVNode("div", _hoisted_58$1, [_cache[30] || (_cache[30] = createBaseVNode("p", { class: "text-sm font-medium text-blue-900 dark:text-blue-400 mb-2" }, "💡 Recommendation", -1)), createBaseVNode("p", _hoisted_59$1, toDisplayString($options.getRecommendation($data.selectedCheck)), 1)])
			]),
			createBaseVNode("div", _hoisted_60$1, [createBaseVNode("button", {
				onClick: _cache[2] || (_cache[2] = ($event) => $data.selectedCheck = null),
				class: "px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg"
			}, "Close")])
		])])) : createCommentVNode("", true)
	]);
}
var _sfc_main$23 = {
	name: "Analytics",
	components: {
		DateRangePicker: DateRangePicker_default,
		ExportButton: ExportButton_default,
		FinancialAnalytics: FinancialAnalytics_default,
		RFMSegmentation: RFMSegmentation_default,
		CohortAnalysis: CohortAnalysis_default,
		FunnelAnalysis: FunnelAnalysis_default,
		ChurnPrediction: ChurnPrediction_default,
		RevenueForecast: RevenueForecast_default,
		NetworkAnalytics: NetworkAnalytics_default,
		DashboardBuilder: DashboardBuilder_default,
		ABTesting: ABTesting_default,
		CustomerHealth: CustomerHealth_default,
		AuditLogs: AuditLogs_default,
		DataQuality: /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$24, [["render", _sfc_render$24]])
	},
	setup() {
		const { loading, makeRequest } = useApi();
		return {
			loading,
			makeRequest
		};
	},
	data() {
		return {
			activeTab: "financial",
			tabs: [
				{
					id: "financial",
					name: "Financial"
				},
				{
					id: "customers",
					name: "Customers"
				},
				{
					id: "retention",
					name: "Retention"
				},
				{
					id: "predictive",
					name: "Predictive"
				},
				{
					id: "network",
					name: "Network"
				},
				{
					id: "testing",
					name: "A/B Testing"
				},
				{
					id: "health",
					name: "Health"
				},
				{
					id: "audit",
					name: "Audit"
				},
				{
					id: "quality",
					name: "Quality"
				},
				{
					id: "builder",
					name: "Builder"
				}
			],
			dateRange: {},
			financialMetrics: {},
			packagePerformance: [],
			rfmSegments: [],
			rfmSummary: {},
			cohortData: [],
			funnelData: {},
			churnData: {},
			forecastData: {},
			networkData: {},
			abTestData: {},
			healthData: {},
			auditData: {},
			qualityData: {}
		};
	},
	computed: { exportData() {
		return {
			financial: this.financialMetrics,
			packages: this.packagePerformance,
			rfm: {
				segments: this.rfmSegments,
				summary: this.rfmSummary
			},
			cohorts: this.cohortData,
			funnel: this.funnelData,
			churn: this.churnData,
			forecast: this.forecastData,
			network: this.networkData
		};
	} },
	async mounted() {
		await this.fetchAllData();
	},
	methods: {
		handleDateChange(range) {
			this.dateRange = range;
			this.fetchAllData();
		},
		async fetchAllData() {
			await Promise.all([
				this.fetchFinancialAnalytics(),
				this.fetchRFMSegmentation(),
				this.fetchCohortAnalysis(),
				this.fetchFunnelAnalysis(),
				this.fetchChurnPrediction(),
				this.fetchRevenueForecast(),
				this.fetchNetworkAnalytics(),
				this.fetchABTesting(),
				this.fetchCustomerHealth(),
				this.fetchAuditLogs(),
				this.fetchDataQuality()
			]);
		},
		async fetchFinancialAnalytics() {
			try {
				const data = await this.makeRequest("get", "suapi/dashboard-metrics/financial-analytics/");
				this.financialMetrics = {
					mrr: data.mrr,
					arr: data.arr,
					arpu: data.arpu,
					ltv: data.ltv,
					growth_rate: data.growth_rate
				};
				this.packagePerformance = data.package_performance || [];
			} catch (error) {
				console.error("Error fetching financial analytics:", error);
			}
		},
		async fetchRFMSegmentation() {
			try {
				const data = await this.makeRequest("get", "suapi/dashboard-metrics/rfm-segmentation/");
				this.rfmSegments = data.segments || [];
				this.rfmSummary = data.summary || {};
			} catch (error) {
				console.error("Error fetching RFM segmentation:", error);
			}
		},
		async fetchCohortAnalysis() {
			try {
				this.cohortData = (await this.makeRequest("get", "suapi/dashboard-metrics/cohort-analysis/")).data || [];
			} catch (error) {
				console.error("Error fetching cohort analysis:", error);
			}
		},
		async fetchFunnelAnalysis() {
			try {
				this.funnelData = await this.makeRequest("get", "suapi/dashboard-metrics/funnel-analysis/");
			} catch (error) {
				console.error("Error fetching funnel analysis:", error);
			}
		},
		async fetchChurnPrediction() {
			try {
				this.churnData = await this.makeRequest("get", "suapi/dashboard-metrics/churn-prediction/");
			} catch (error) {
				console.error("Error fetching churn prediction:", error);
			}
		},
		async fetchRevenueForecast() {
			try {
				this.forecastData = await this.makeRequest("get", "suapi/dashboard-metrics/revenue-forecast/");
				console.log("Revenue Forecast Data:", JSON.parse(JSON.stringify(this.forecastData)));
				console.log("Historical:", this.forecastData.historical);
				console.log("Forecast:", this.forecastData.forecast);
			} catch (error) {
				console.error("Error fetching revenue forecast:", error);
			}
		},
		async fetchNetworkAnalytics() {
			try {
				this.networkData = await this.makeRequest("get", "suapi/dashboard-metrics/network-analytics/");
			} catch (error) {
				console.error("Error fetching network analytics:", error);
			}
		},
		async fetchABTesting() {
			try {
				this.abTestData = await this.makeRequest("get", "suapi/dashboard-metrics/ab-testing/");
			} catch (error) {
				console.error("Error fetching A/B testing:", error);
			}
		},
		async fetchCustomerHealth() {
			try {
				this.healthData = await this.makeRequest("get", "suapi/dashboard-metrics/customer-health/");
			} catch (error) {
				console.error("Error fetching customer health:", error);
			}
		},
		async fetchAuditLogs() {
			try {
				this.auditData = await this.makeRequest("get", "suapi/dashboard-metrics/audit-logs/");
			} catch (error) {
				console.error("Error fetching audit logs:", error);
			}
		},
		async fetchDataQuality() {
			try {
				this.qualityData = await this.makeRequest("get", "suapi/dashboard-metrics/data-quality/");
			} catch (error) {
				console.error("Error fetching data quality:", error);
			}
		},
		refreshData() {
			this.fetchAllData();
		}
	}
};
var _hoisted_1$23 = { class: "space-y-6 animate-fade-in" };
var _hoisted_2$23 = { class: "flex items-center justify-between" };
var _hoisted_3$23 = { class: "flex items-center gap-3" };
var _hoisted_4$23 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-2" };
var _hoisted_5$23 = { class: "flex gap-2" };
var _hoisted_6$23 = ["onClick"];
var _hoisted_7$23 = { key: 0 };
var _hoisted_8$23 = { key: 1 };
var _hoisted_9$21 = { key: 2 };
var _hoisted_10$19 = { class: "grid grid-cols-1 lg:grid-cols-2 gap-4" };
var _hoisted_11$18 = { key: 3 };
var _hoisted_12$18 = { class: "grid grid-cols-1 lg:grid-cols-2 gap-4" };
var _hoisted_13$18 = { key: 4 };
var _hoisted_14$18 = { key: 5 };
var _hoisted_15$18 = { key: 6 };
var _hoisted_16$18 = { key: 7 };
var _hoisted_17$18 = { key: 8 };
var _hoisted_18$18 = { key: 9 };
function _sfc_render$23(_ctx, _cache, $props, $setup, $data, $options) {
	const _component_DateRangePicker = resolveComponent("DateRangePicker");
	const _component_ExportButton = resolveComponent("ExportButton");
	const _component_FinancialAnalytics = resolveComponent("FinancialAnalytics");
	const _component_RFMSegmentation = resolveComponent("RFMSegmentation");
	const _component_CohortAnalysis = resolveComponent("CohortAnalysis");
	const _component_FunnelAnalysis = resolveComponent("FunnelAnalysis");
	const _component_ChurnPrediction = resolveComponent("ChurnPrediction");
	const _component_RevenueForecast = resolveComponent("RevenueForecast");
	const _component_NetworkAnalytics = resolveComponent("NetworkAnalytics");
	const _component_DashboardBuilder = resolveComponent("DashboardBuilder");
	const _component_ABTesting = resolveComponent("ABTesting");
	const _component_CustomerHealth = resolveComponent("CustomerHealth");
	const _component_AuditLogs = resolveComponent("AuditLogs");
	const _component_DataQuality = resolveComponent("DataQuality");
	return openBlock(), createElementBlock("div", _hoisted_1$23, [
		createBaseVNode("div", _hoisted_2$23, [_cache[2] || (_cache[2] = createBaseVNode("div", null, [createBaseVNode("h1", { class: "text-2xl font-semibold text-slate-900 dark:text-white" }, "Advanced Analytics"), createBaseVNode("p", { class: "text-sm text-slate-500 dark:text-slate-400 mt-1" }, "Deep insights into customer behavior and financial performance")], -1)), createBaseVNode("div", _hoisted_3$23, [
			createVNode(_component_DateRangePicker, { onChange: $options.handleDateChange }, null, 8, ["onChange"]),
			createVNode(_component_ExportButton, {
				data: $options.exportData,
				filename: "advanced-analytics"
			}, null, 8, ["data"]),
			createBaseVNode("button", {
				onClick: _cache[0] || (_cache[0] = (...args) => $options.refreshData && $options.refreshData(...args)),
				class: normalizeClass(["p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors", { "animate-spin": $setup.loading }])
			}, [..._cache[1] || (_cache[1] = [createBaseVNode("svg", {
				class: "w-5 h-5 text-slate-600 dark:text-slate-400",
				fill: "none",
				stroke: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
			})], -1)])], 2)
		])]),
		createBaseVNode("div", _hoisted_4$23, [createBaseVNode("div", _hoisted_5$23, [(openBlock(true), createElementBlock(Fragment, null, renderList($data.tabs, (tab) => {
			return openBlock(), createElementBlock("button", {
				key: tab.id,
				onClick: ($event) => $data.activeTab = tab.id,
				class: normalizeClass(["flex-1 px-4 py-2 text-sm rounded-lg transition-colors", $data.activeTab === tab.id ? "bg-blue-500 text-white" : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700"])
			}, toDisplayString(tab.name), 11, _hoisted_6$23);
		}), 128))])]),
		$data.activeTab === "financial" ? (openBlock(), createElementBlock("div", _hoisted_7$23, [createVNode(_component_FinancialAnalytics, {
			metrics: $data.financialMetrics,
			packages: $data.packagePerformance,
			loading: $setup.loading
		}, null, 8, [
			"metrics",
			"packages",
			"loading"
		])])) : createCommentVNode("", true),
		$data.activeTab === "customers" ? (openBlock(), createElementBlock("div", _hoisted_8$23, [createVNode(_component_RFMSegmentation, {
			segments: $data.rfmSegments,
			summary: $data.rfmSummary,
			loading: $setup.loading
		}, null, 8, [
			"segments",
			"summary",
			"loading"
		])])) : createCommentVNode("", true),
		$data.activeTab === "retention" ? (openBlock(), createElementBlock("div", _hoisted_9$21, [createBaseVNode("div", _hoisted_10$19, [createVNode(_component_CohortAnalysis, {
			data: $data.cohortData,
			loading: $setup.loading
		}, null, 8, ["data", "loading"]), createVNode(_component_FunnelAnalysis, {
			data: $data.funnelData,
			loading: $setup.loading
		}, null, 8, ["data", "loading"])])])) : createCommentVNode("", true),
		$data.activeTab === "predictive" ? (openBlock(), createElementBlock("div", _hoisted_11$18, [createBaseVNode("div", _hoisted_12$18, [createVNode(_component_ChurnPrediction, {
			data: $data.churnData,
			loading: $setup.loading
		}, null, 8, ["data", "loading"]), createVNode(_component_RevenueForecast, {
			data: $data.forecastData,
			loading: $setup.loading
		}, null, 8, ["data", "loading"])])])) : createCommentVNode("", true),
		$data.activeTab === "network" ? (openBlock(), createElementBlock("div", _hoisted_13$18, [createVNode(_component_NetworkAnalytics, {
			data: $data.networkData,
			loading: $setup.loading
		}, null, 8, ["data", "loading"])])) : createCommentVNode("", true),
		$data.activeTab === "builder" ? (openBlock(), createElementBlock("div", _hoisted_14$18, [createVNode(_component_DashboardBuilder)])) : createCommentVNode("", true),
		$data.activeTab === "testing" ? (openBlock(), createElementBlock("div", _hoisted_15$18, [createVNode(_component_ABTesting, {
			data: $data.abTestData,
			loading: $setup.loading,
			onRefresh: $options.fetchABTesting
		}, null, 8, [
			"data",
			"loading",
			"onRefresh"
		])])) : createCommentVNode("", true),
		$data.activeTab === "health" ? (openBlock(), createElementBlock("div", _hoisted_16$18, [createVNode(_component_CustomerHealth, {
			data: $data.healthData,
			loading: $setup.loading
		}, null, 8, ["data", "loading"])])) : createCommentVNode("", true),
		$data.activeTab === "audit" ? (openBlock(), createElementBlock("div", _hoisted_17$18, [createVNode(_component_AuditLogs, {
			data: $data.auditData,
			loading: $setup.loading
		}, null, 8, ["data", "loading"])])) : createCommentVNode("", true),
		$data.activeTab === "quality" ? (openBlock(), createElementBlock("div", _hoisted_18$18, [createVNode(_component_DataQuality, {
			data: $data.qualityData,
			loading: $setup.loading
		}, null, 8, ["data", "loading"])])) : createCommentVNode("", true)
	]);
}
var Analytics_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$23, [["render", _sfc_render$23], ["__scopeId", "data-v-477b9121"]]);
var _sfc_main$22 = {
	name: "ConfirmDialog",
	props: {
		show: Boolean,
		type: {
			type: String,
			default: "info"
		},
		title: {
			type: String,
			default: "Confirm Action"
		},
		message: {
			type: String,
			default: "Are you sure?"
		},
		confirmText: {
			type: String,
			default: "Confirm"
		},
		cancelText: {
			type: String,
			default: "Cancel"
		}
	},
	emits: ["confirm", "cancel"],
	setup(props, { emit }) {
		const iconBg = computed(() => {
			const classes = {
				danger: "bg-red-100 dark:bg-red-500/20",
				warning: "bg-amber-100 dark:bg-amber-500/20",
				info: "bg-blue-100 dark:bg-blue-500/20"
			};
			return classes[props.type] || classes.info;
		});
		const iconColor = computed(() => {
			const classes = {
				danger: "text-red-600 dark:text-red-400",
				warning: "text-amber-600 dark:text-amber-400",
				info: "text-blue-600 dark:text-blue-400"
			};
			return classes[props.type] || classes.info;
		});
		const confirmBtnClass = computed(() => {
			const classes = {
				danger: "bg-red-500 hover:bg-red-600",
				warning: "bg-amber-500 hover:bg-amber-600",
				info: "bg-blue-500 hover:bg-blue-600"
			};
			return classes[props.type] || classes.info;
		});
		const confirm$1 = () => emit("confirm");
		const cancel = () => emit("cancel");
		return {
			iconBg,
			iconColor,
			confirmBtnClass,
			confirm: confirm$1,
			cancel
		};
	}
};
var _hoisted_1$22 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-sm w-full p-5" };
var _hoisted_2$22 = { class: "flex items-start gap-3 mb-4" };
var _hoisted_3$22 = {
	key: 0,
	"stroke-linecap": "round",
	"stroke-linejoin": "round",
	"stroke-width": "2",
	d: "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
};
var _hoisted_4$22 = {
	key: 1,
	"stroke-linecap": "round",
	"stroke-linejoin": "round",
	"stroke-width": "2",
	d: "M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
};
var _hoisted_5$22 = {
	key: 2,
	"stroke-linecap": "round",
	"stroke-linejoin": "round",
	"stroke-width": "2",
	d: "M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
};
var _hoisted_6$22 = { class: "flex-1" };
var _hoisted_7$22 = { class: "text-sm font-semibold text-slate-900 dark:text-white mb-1" };
var _hoisted_8$22 = { class: "text-xs text-slate-600 dark:text-slate-400" };
var _hoisted_9$20 = { class: "flex gap-2" };
function _sfc_render$22(_ctx, _cache, $props, $setup, $data, $options) {
	return $props.show ? (openBlock(), createElementBlock("div", {
		key: 0,
		class: "fixed inset-0 bg-black/60 backdrop-blur-sm z-[70] flex items-center justify-center p-4",
		onClick: _cache[2] || (_cache[2] = withModifiers((...args) => $setup.cancel && $setup.cancel(...args), ["self"]))
	}, [createBaseVNode("div", _hoisted_1$22, [createBaseVNode("div", _hoisted_2$22, [createBaseVNode("div", { class: normalizeClass(["w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0", $setup.iconBg]) }, [(openBlock(), createElementBlock("svg", {
		class: normalizeClass(["w-5 h-5", $setup.iconColor]),
		fill: "none",
		stroke: "currentColor",
		viewBox: "0 0 24 24"
	}, [$props.type === "danger" ? (openBlock(), createElementBlock("path", _hoisted_3$22)) : $props.type === "warning" ? (openBlock(), createElementBlock("path", _hoisted_4$22)) : (openBlock(), createElementBlock("path", _hoisted_5$22))], 2))], 2), createBaseVNode("div", _hoisted_6$22, [createBaseVNode("h3", _hoisted_7$22, toDisplayString($props.title), 1), createBaseVNode("p", _hoisted_8$22, toDisplayString($props.message), 1)])]), createBaseVNode("div", _hoisted_9$20, [createBaseVNode("button", {
		onClick: _cache[0] || (_cache[0] = (...args) => $setup.cancel && $setup.cancel(...args)),
		class: "flex-1 px-3 py-2 text-xs font-medium bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg transition-colors"
	}, toDisplayString($props.cancelText), 1), createBaseVNode("button", {
		onClick: _cache[1] || (_cache[1] = (...args) => $setup.confirm && $setup.confirm(...args)),
		class: normalizeClass(["flex-1 px-3 py-2 text-xs font-medium text-white rounded-lg transition-colors", $setup.confirmBtnClass])
	}, toDisplayString($props.confirmText), 3)])])])) : createCommentVNode("", true);
}
var ConfirmDialog_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$22, [["render", _sfc_render$22]]);
var _sfc_main$21 = {
	name: "ClientDetailModal",
	components: { ConfirmDialog: ConfirmDialog_default },
	props: {
		show: Boolean,
		client: Object
	},
	emits: ["close", "refresh"],
	setup(props, { emit }) {
		const { makeRequest } = useApi();
		const activeTab = ref("general");
		const profile = ref({
			devices: [],
			sessions: [],
			transactions: [],
			vouchers: [],
			stats: {}
		});
		const analytics = ref({});
		const showBalanceModal = ref(false);
		const showPointsModal = ref(false);
		const balanceAmount = ref(0);
		const balanceReason = ref("");
		const pointsAmount = ref(0);
		const pointsReason = ref("");
		const tabs = [{
			id: "general",
			label: "General"
		}, {
			id: "advanced",
			label: "Advanced"
		}];
		const fetchProfile = async () => {
			if (!props.client?.id) return;
			try {
				profile.value = await makeRequest("get", `suapi/clients/${props.client.id}/profile/`);
				try {
					analytics.value = await makeRequest("get", `suapi/clients/${props.client.id}/analytics/`);
				} catch (error) {
					console.error("Error fetching analytics:", error);
					analytics.value = {
						ltv: 0,
						engagement_score: 0,
						churn_risk: "unknown",
						avg_transaction: 0
					};
				}
			} catch (error) {
				console.error("Error fetching profile:", error);
			}
		};
		const adjustBalance = async () => {
			try {
				await makeRequest("post", `suapi/clients/${props.client.id}/adjust_balance/`, {
					amount: balanceAmount.value,
					reason: balanceReason.value
				});
				showBalanceModal.value = false;
				emit("refresh");
				fetchProfile();
			} catch (error) {
				console.error("Error adjusting balance:", error);
			}
		};
		const awardPoints = async () => {
			try {
				await makeRequest("post", `suapi/clients/${props.client.id}/award_points/`, {
					points: pointsAmount.value,
					description: pointsReason.value
				});
				showPointsModal.value = false;
				emit("refresh");
				fetchProfile();
			} catch (error) {
				console.error("Error awarding points:", error);
			}
		};
		const confirmDialog = reactive({
			show: false,
			type: "info",
			title: "",
			message: "",
			confirmText: "Confirm",
			onConfirm: () => {}
		});
		const toggleSuspend = () => {
			const action = props.client.status === "suspended" ? "activate" : "suspend";
			confirmDialog.show = true;
			confirmDialog.type = action === "suspend" ? "warning" : "info";
			confirmDialog.title = action === "suspend" ? "Suspend Client" : "Activate Client";
			confirmDialog.message = action === "suspend" ? "This will temporarily disable the client account." : "This will reactivate the client account.";
			confirmDialog.confirmText = action === "suspend" ? "Suspend" : "Activate";
			confirmDialog.onConfirm = async () => {
				try {
					await makeRequest("post", `suapi/clients/${props.client.id}/${action}/`, { reason: "Admin action" });
					confirmDialog.show = false;
					emit("refresh");
					emit("close");
				} catch (error) {
					console.error(`Error ${action}ing client:`, error);
				}
			};
		};
		const forceLogout = () => {
			confirmDialog.show = true;
			confirmDialog.type = "danger";
			confirmDialog.title = "Force Logout";
			confirmDialog.message = "This will end all active sessions for this client.";
			confirmDialog.confirmText = "Logout";
			confirmDialog.onConfirm = async () => {
				try {
					await makeRequest("post", `suapi/clients/${props.client.id}/force_logout/`, { reason: "Admin action" });
					confirmDialog.show = false;
					fetchProfile();
				} catch (error) {
					console.error("Error forcing logout:", error);
				}
			};
		};
		const getUserIcon = () => {
			return `<svg class="w-10 h-10 text-slate-400 dark:text-slate-500" fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>`;
		};
		const formatNumber = (num) => new Intl.NumberFormat().format(num || 0);
		const formatDate = (date) => date ? new Date(date).toLocaleDateString() : "N/A";
		const formatBytes = (bytes) => {
			if (!bytes) return "0 B";
			const k = 1024;
			const sizes = [
				"B",
				"KB",
				"MB",
				"GB",
				"TB"
			];
			const i = Math.floor(Math.log(bytes) / Math.log(k));
			return Math.round(bytes / Math.pow(k, i) * 100) / 100 + " " + sizes[i];
		};
		const getTierBadge = (tier) => {
			const badges = {
				"basic": "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300",
				"premium": "bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400",
				"business": "bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400",
				"enterprise": "bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400"
			};
			return badges[tier] || badges.basic;
		};
		const getStatusBadge = (status) => {
			const badges = {
				"active": "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400",
				"inactive": "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400",
				"suspended": "bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400",
				"banned": "bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400"
			};
			return badges[status] || badges.inactive;
		};
		watch(() => props.show, (newVal) => {
			if (newVal) fetchProfile();
		});
		return {
			activeTab,
			tabs,
			profile,
			analytics,
			showBalanceModal,
			showPointsModal,
			balanceAmount,
			balanceReason,
			pointsAmount,
			pointsReason,
			confirmDialog,
			adjustBalance,
			awardPoints,
			toggleSuspend,
			forceLogout,
			getUserIcon,
			formatNumber,
			formatDate,
			formatBytes,
			getTierBadge,
			getStatusBadge
		};
	}
};
var _hoisted_1$21 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-3xl w-full max-h-[80vh] overflow-hidden" };
var _hoisted_2$21 = { class: "flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-700" };
var _hoisted_3$21 = { class: "flex items-center gap-3" };
var _hoisted_4$21 = ["innerHTML"];
var _hoisted_5$21 = { class: "text-base font-semibold text-slate-900 dark:text-white" };
var _hoisted_6$21 = { class: "text-xs text-slate-500 dark:text-slate-400" };
var _hoisted_7$21 = { class: "border-b border-slate-200 dark:border-slate-700 px-4" };
var _hoisted_8$21 = { class: "flex gap-3" };
var _hoisted_9$19 = ["onClick"];
var _hoisted_10$18 = { class: "p-4 overflow-y-auto max-h-[calc(80vh-140px)]" };
var _hoisted_11$17 = {
	key: 0,
	class: "space-y-3"
};
var _hoisted_12$17 = { class: "flex items-start gap-3 mb-3" };
var _hoisted_13$17 = {
	key: 0,
	class: "w-16 h-16 rounded-lg overflow-hidden"
};
var _hoisted_14$17 = ["src"];
var _hoisted_15$17 = ["innerHTML"];
var _hoisted_16$17 = { class: "flex-1 grid grid-cols-2 md:grid-cols-3 gap-2" };
var _hoisted_17$17 = { class: "p-2 bg-blue-50 dark:bg-blue-500/10 rounded-lg" };
var _hoisted_18$17 = { class: "text-sm font-bold text-blue-700 dark:text-blue-300" };
var _hoisted_19$16 = { class: "p-2 bg-purple-50 dark:bg-purple-500/10 rounded-lg" };
var _hoisted_20$16 = { class: "text-sm font-bold text-purple-700 dark:text-purple-300" };
var _hoisted_21$16 = { class: "p-2 bg-emerald-50 dark:bg-emerald-500/10 rounded-lg col-span-2 md:col-span-1" };
var _hoisted_22$16 = { class: "text-sm font-bold text-emerald-700 dark:text-emerald-300" };
var _hoisted_23$16 = { class: "grid grid-cols-2 gap-x-4 gap-y-2 text-xs" };
var _hoisted_24$16 = { class: "font-medium text-slate-900 dark:text-white ml-2" };
var _hoisted_25$16 = { class: "font-medium text-slate-900 dark:text-white ml-2" };
var _hoisted_26$16 = { class: "font-medium text-slate-900 dark:text-white ml-2" };
var _hoisted_27$15 = { class: "font-medium text-slate-900 dark:text-white ml-2" };
var _hoisted_28$15 = { class: "font-medium text-slate-900 dark:text-white ml-2" };
var _hoisted_29$15 = { class: "font-medium text-slate-900 dark:text-white ml-2" };
var _hoisted_30$15 = { class: "font-medium text-slate-900 dark:text-white ml-2" };
var _hoisted_31$15 = { class: "font-medium text-slate-900 dark:text-white ml-2" };
var _hoisted_32$15 = { class: "font-medium text-slate-900 dark:text-white ml-2" };
var _hoisted_33$15 = { class: "font-medium text-slate-900 dark:text-white ml-2" };
var _hoisted_34$15 = { class: "grid grid-cols-4 gap-2 pt-2 border-t border-slate-200 dark:border-slate-700" };
var _hoisted_35$15 = { class: "text-center p-1.5 bg-slate-50 dark:bg-slate-700/50 rounded" };
var _hoisted_36$15 = { class: "text-sm font-bold text-slate-900 dark:text-white" };
var _hoisted_37$15 = { class: "text-center p-1.5 bg-slate-50 dark:bg-slate-700/50 rounded" };
var _hoisted_38$15 = { class: "text-sm font-bold text-slate-900 dark:text-white" };
var _hoisted_39$15 = { class: "text-center p-1.5 bg-slate-50 dark:bg-slate-700/50 rounded" };
var _hoisted_40$15 = { class: "text-sm font-bold text-slate-900 dark:text-white" };
var _hoisted_41$14 = { class: "text-center p-1.5 bg-slate-50 dark:bg-slate-700/50 rounded" };
var _hoisted_42$12 = { class: "text-sm font-bold text-slate-900 dark:text-white" };
var _hoisted_43$11 = {
	key: 1,
	class: "space-y-3"
};
var _hoisted_44$11 = { class: "grid grid-cols-2 gap-2" };
var _hoisted_45$8 = { class: "p-2 bg-slate-50 dark:bg-slate-700/50 rounded-lg" };
var _hoisted_46$8 = { class: "text-base font-bold text-slate-900 dark:text-white" };
var _hoisted_47$7 = { class: "p-2 bg-slate-50 dark:bg-slate-700/50 rounded-lg" };
var _hoisted_48$4 = { class: "text-base font-bold text-slate-900 dark:text-white" };
var _hoisted_49$4 = { class: "p-2 bg-slate-50 dark:bg-slate-700/50 rounded-lg" };
var _hoisted_50$4 = { class: "p-2 bg-slate-50 dark:bg-slate-700/50 rounded-lg" };
var _hoisted_51$4 = { class: "text-base font-bold text-slate-900 dark:text-white" };
var _hoisted_52$3 = { class: "grid grid-cols-2 gap-2" };
var _hoisted_53$3 = { class: "text-xs font-medium text-amber-700 dark:text-amber-400" };
var _hoisted_54$2 = { class: "text-[10px] text-amber-600 dark:text-amber-500 mt-0.5" };
var _hoisted_55$1 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-sm w-full p-5" };
var _hoisted_56 = { class: "flex items-center gap-3 mb-4" };
var _hoisted_57 = { class: "text-[10px] text-slate-500 dark:text-slate-400" };
var _hoisted_58 = { class: "space-y-2.5 mb-4" };
var _hoisted_59 = { class: "flex gap-2" };
var _hoisted_60 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-sm w-full p-5" };
var _hoisted_61 = { class: "flex items-center gap-3 mb-4" };
var _hoisted_62 = { class: "text-[10px] text-slate-500 dark:text-slate-400" };
var _hoisted_63 = { class: "space-y-2.5 mb-4" };
var _hoisted_64 = { class: "flex gap-2" };
function _sfc_render$21(_ctx, _cache, $props, $setup, $data, $options) {
	const _component_ConfirmDialog = resolveComponent("ConfirmDialog");
	return $props.show ? (openBlock(), createElementBlock("div", {
		key: 0,
		class: "fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4",
		onClick: _cache[17] || (_cache[17] = withModifiers(($event) => _ctx.$emit("close"), ["self"]))
	}, [
		createBaseVNode("div", _hoisted_1$21, [
			createBaseVNode("div", _hoisted_2$21, [createBaseVNode("div", _hoisted_3$21, [createBaseVNode("div", {
				class: "w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-700 flex items-center justify-center",
				innerHTML: $setup.getUserIcon()
			}, null, 8, _hoisted_4$21), createBaseVNode("div", null, [createBaseVNode("h2", _hoisted_5$21, toDisplayString($props.client.user_username), 1), createBaseVNode("p", _hoisted_6$21, toDisplayString($props.client.account), 1)])]), createBaseVNode("button", {
				onClick: _cache[0] || (_cache[0] = ($event) => _ctx.$emit("close")),
				class: "p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
			}, [..._cache[18] || (_cache[18] = [createBaseVNode("svg", {
				class: "w-4 h-4 text-slate-600 dark:text-slate-300",
				fill: "none",
				stroke: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M6 18L18 6M6 6l12 12"
			})], -1)])])]),
			createBaseVNode("div", _hoisted_7$21, [createBaseVNode("div", _hoisted_8$21, [(openBlock(true), createElementBlock(Fragment, null, renderList($setup.tabs, (tab) => {
				return openBlock(), createElementBlock("button", {
					key: tab.id,
					onClick: ($event) => $setup.activeTab = tab.id,
					class: normalizeClass(["px-3 py-2 text-xs font-medium border-b-2 transition-colors", $setup.activeTab === tab.id ? "border-blue-500 text-blue-600 dark:text-blue-400" : "border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"])
				}, toDisplayString(tab.label), 11, _hoisted_9$19);
			}), 128))])]),
			createBaseVNode("div", _hoisted_10$18, [$setup.activeTab === "general" ? (openBlock(), createElementBlock("div", _hoisted_11$17, [
				createBaseVNode("div", _hoisted_12$17, [$props.client.profile_image ? (openBlock(), createElementBlock("div", _hoisted_13$17, [createBaseVNode("img", {
					src: $props.client.profile_image,
					alt: "Profile",
					class: "w-full h-full object-cover",
					onError: _cache[1] || (_cache[1] = ($event) => $event.target.parentElement.innerHTML = $setup.getUserIcon())
				}, null, 40, _hoisted_14$17)])) : (openBlock(), createElementBlock("div", {
					key: 1,
					class: "w-16 h-16 rounded-lg bg-slate-100 dark:bg-slate-700 flex items-center justify-center",
					innerHTML: $setup.getUserIcon()
				}, null, 8, _hoisted_15$17)), createBaseVNode("div", _hoisted_16$17, [
					createBaseVNode("div", _hoisted_17$17, [_cache[19] || (_cache[19] = createBaseVNode("p", { class: "text-[10px] text-blue-600 dark:text-blue-400" }, "Balance", -1)), createBaseVNode("p", _hoisted_18$17, "KSh " + toDisplayString($setup.formatNumber($props.client.balance)), 1)]),
					createBaseVNode("div", _hoisted_19$16, [_cache[20] || (_cache[20] = createBaseVNode("p", { class: "text-[10px] text-purple-600 dark:text-purple-400" }, "Points", -1)), createBaseVNode("p", _hoisted_20$16, toDisplayString($props.client.reward_points), 1)]),
					createBaseVNode("div", _hoisted_21$16, [_cache[21] || (_cache[21] = createBaseVNode("p", { class: "text-[10px] text-emerald-600 dark:text-emerald-400" }, "Spent", -1)), createBaseVNode("p", _hoisted_22$16, "KSh " + toDisplayString($setup.formatNumber($props.client.total_spent)), 1)])
				])]),
				createBaseVNode("div", _hoisted_23$16, [
					createBaseVNode("div", null, [
						_cache[22] || (_cache[22] = createBaseVNode("span", { class: "text-slate-500 dark:text-slate-400" }, "Account:", -1)),
						_cache[23] || (_cache[23] = createTextVNode()),
						createBaseVNode("span", _hoisted_24$16, toDisplayString($props.client.account), 1)
					]),
					createBaseVNode("div", null, [
						_cache[24] || (_cache[24] = createBaseVNode("span", { class: "text-slate-500 dark:text-slate-400" }, "Phone:", -1)),
						_cache[25] || (_cache[25] = createTextVNode()),
						createBaseVNode("span", _hoisted_25$16, toDisplayString($props.client.phone_number), 1)
					]),
					createBaseVNode("div", null, [
						_cache[26] || (_cache[26] = createBaseVNode("span", { class: "text-slate-500 dark:text-slate-400" }, "Email:", -1)),
						_cache[27] || (_cache[27] = createTextVNode()),
						createBaseVNode("span", _hoisted_26$16, toDisplayString($props.client.user_email || "N/A"), 1)
					]),
					createBaseVNode("div", null, [
						_cache[28] || (_cache[28] = createBaseVNode("span", { class: "text-slate-500 dark:text-slate-400" }, "Display Name:", -1)),
						_cache[29] || (_cache[29] = createTextVNode()),
						createBaseVNode("span", _hoisted_27$15, toDisplayString($props.client.display_name || "N/A"), 1)
					]),
					createBaseVNode("div", null, [
						_cache[30] || (_cache[30] = createBaseVNode("span", { class: "text-slate-500 dark:text-slate-400" }, "Tier:", -1)),
						_cache[31] || (_cache[31] = createTextVNode()),
						createBaseVNode("span", { class: normalizeClass(["px-2 py-0.5 text-xs rounded-full ml-2", $setup.getTierBadge($props.client.account_tier)]) }, toDisplayString($props.client.account_tier), 3)
					]),
					createBaseVNode("div", null, [
						_cache[32] || (_cache[32] = createBaseVNode("span", { class: "text-slate-500 dark:text-slate-400" }, "Status:", -1)),
						_cache[33] || (_cache[33] = createTextVNode()),
						createBaseVNode("span", { class: normalizeClass(["px-2 py-0.5 text-xs rounded-full ml-2", $setup.getStatusBadge($props.client.status)]) }, toDisplayString($props.client.status), 3)
					]),
					createBaseVNode("div", null, [
						_cache[34] || (_cache[34] = createBaseVNode("span", { class: "text-slate-500 dark:text-slate-400" }, "Reward Tier:", -1)),
						_cache[35] || (_cache[35] = createTextVNode()),
						createBaseVNode("span", _hoisted_28$15, toDisplayString($props.client.reward_tier), 1)
					]),
					createBaseVNode("div", null, [
						_cache[36] || (_cache[36] = createBaseVNode("span", { class: "text-slate-500 dark:text-slate-400" }, "Credit Limit:", -1)),
						_cache[37] || (_cache[37] = createTextVNode()),
						createBaseVNode("span", _hoisted_29$15, "KSh " + toDisplayString($setup.formatNumber($props.client.credit_limit)), 1)
					]),
					createBaseVNode("div", null, [
						_cache[38] || (_cache[38] = createBaseVNode("span", { class: "text-slate-500 dark:text-slate-400" }, "Data Used:", -1)),
						_cache[39] || (_cache[39] = createTextVNode()),
						createBaseVNode("span", _hoisted_30$15, toDisplayString($setup.formatBytes($props.client.lifetime_data_used)), 1)
					]),
					createBaseVNode("div", null, [
						_cache[40] || (_cache[40] = createBaseVNode("span", { class: "text-slate-500 dark:text-slate-400" }, "Joined:", -1)),
						_cache[41] || (_cache[41] = createTextVNode()),
						createBaseVNode("span", _hoisted_31$15, toDisplayString($setup.formatDate($props.client.created_at)), 1)
					]),
					createBaseVNode("div", null, [
						_cache[42] || (_cache[42] = createBaseVNode("span", { class: "text-slate-500 dark:text-slate-400" }, "Last Login:", -1)),
						_cache[43] || (_cache[43] = createTextVNode()),
						createBaseVNode("span", _hoisted_32$15, toDisplayString($setup.formatDate($props.client.last_login)), 1)
					]),
					createBaseVNode("div", null, [
						_cache[44] || (_cache[44] = createBaseVNode("span", { class: "text-slate-500 dark:text-slate-400" }, "2FA:", -1)),
						_cache[45] || (_cache[45] = createTextVNode()),
						createBaseVNode("span", _hoisted_33$15, toDisplayString($props.client.two_factor_enabled ? "Enabled" : "Disabled"), 1)
					])
				]),
				createBaseVNode("div", _hoisted_34$15, [
					createBaseVNode("div", _hoisted_35$15, [_cache[46] || (_cache[46] = createBaseVNode("p", { class: "text-[10px] text-slate-500 dark:text-slate-400" }, "Devices", -1)), createBaseVNode("p", _hoisted_36$15, toDisplayString($setup.profile.stats?.total_devices || 0), 1)]),
					createBaseVNode("div", _hoisted_37$15, [_cache[47] || (_cache[47] = createBaseVNode("p", { class: "text-[10px] text-slate-500 dark:text-slate-400" }, "Sessions", -1)), createBaseVNode("p", _hoisted_38$15, toDisplayString($setup.profile.stats?.active_sessions || 0), 1)]),
					createBaseVNode("div", _hoisted_39$15, [_cache[48] || (_cache[48] = createBaseVNode("p", { class: "text-[10px] text-slate-500 dark:text-slate-400" }, "Vouchers", -1)), createBaseVNode("p", _hoisted_40$15, toDisplayString($setup.profile.stats?.total_vouchers || 0), 1)]),
					createBaseVNode("div", _hoisted_41$14, [_cache[49] || (_cache[49] = createBaseVNode("p", { class: "text-[10px] text-slate-500 dark:text-slate-400" }, "Points Earned", -1)), createBaseVNode("p", _hoisted_42$12, toDisplayString($props.client.total_points_earned || 0), 1)])
				])
			])) : createCommentVNode("", true), $setup.activeTab === "advanced" ? (openBlock(), createElementBlock("div", _hoisted_43$11, [createBaseVNode("div", null, [_cache[54] || (_cache[54] = createBaseVNode("h4", { class: "text-xs font-semibold text-slate-900 dark:text-white mb-2" }, "Analytics & Insights", -1)), createBaseVNode("div", _hoisted_44$11, [
				createBaseVNode("div", _hoisted_45$8, [_cache[50] || (_cache[50] = createBaseVNode("p", { class: "text-[10px] text-slate-600 dark:text-slate-400 mb-0.5" }, "Lifetime Value", -1)), createBaseVNode("p", _hoisted_46$8, "KSh " + toDisplayString($setup.formatNumber($setup.analytics.ltv)), 1)]),
				createBaseVNode("div", _hoisted_47$7, [_cache[51] || (_cache[51] = createBaseVNode("p", { class: "text-[10px] text-slate-600 dark:text-slate-400 mb-0.5" }, "Engagement Score", -1)), createBaseVNode("p", _hoisted_48$4, toDisplayString($setup.analytics.engagement_score) + "%", 1)]),
				createBaseVNode("div", _hoisted_49$4, [_cache[52] || (_cache[52] = createBaseVNode("p", { class: "text-[10px] text-slate-600 dark:text-slate-400 mb-0.5" }, "Churn Risk", -1)), createBaseVNode("p", { class: normalizeClass(["text-base font-bold", $setup.analytics.churn_risk === "low" ? "text-emerald-600" : "text-red-600"]) }, toDisplayString($setup.analytics.churn_risk), 3)]),
				createBaseVNode("div", _hoisted_50$4, [_cache[53] || (_cache[53] = createBaseVNode("p", { class: "text-[10px] text-slate-600 dark:text-slate-400 mb-0.5" }, "Avg Transaction", -1)), createBaseVNode("p", _hoisted_51$4, "KSh " + toDisplayString($setup.formatNumber($setup.analytics.avg_transaction)), 1)])
			])]), createBaseVNode("div", null, [_cache[58] || (_cache[58] = createBaseVNode("h4", { class: "text-xs font-semibold text-slate-900 dark:text-white mb-2" }, "Quick Actions", -1)), createBaseVNode("div", _hoisted_52$3, [
				createBaseVNode("button", {
					onClick: _cache[2] || (_cache[2] = ($event) => $setup.showBalanceModal = true),
					class: "p-2.5 bg-blue-50 dark:bg-blue-500/10 hover:bg-blue-100 dark:hover:bg-blue-500/20 rounded-lg text-left transition-colors"
				}, [..._cache[55] || (_cache[55] = [createBaseVNode("p", { class: "text-xs font-medium text-blue-700 dark:text-blue-400" }, "Adjust Balance", -1), createBaseVNode("p", { class: "text-[10px] text-blue-600 dark:text-blue-500 mt-0.5" }, "Add or deduct balance", -1)])]),
				createBaseVNode("button", {
					onClick: _cache[3] || (_cache[3] = ($event) => $setup.showPointsModal = true),
					class: "p-2.5 bg-purple-50 dark:bg-purple-500/10 hover:bg-purple-100 dark:hover:bg-purple-500/20 rounded-lg text-left transition-colors"
				}, [..._cache[56] || (_cache[56] = [createBaseVNode("p", { class: "text-xs font-medium text-purple-700 dark:text-purple-400" }, "Award Points", -1), createBaseVNode("p", { class: "text-[10px] text-purple-600 dark:text-purple-500 mt-0.5" }, "Give reward points", -1)])]),
				createBaseVNode("button", {
					onClick: _cache[4] || (_cache[4] = (...args) => $setup.toggleSuspend && $setup.toggleSuspend(...args)),
					class: "p-2.5 bg-amber-50 dark:bg-amber-500/10 hover:bg-amber-100 dark:hover:bg-amber-500/20 rounded-lg text-left transition-colors"
				}, [createBaseVNode("p", _hoisted_53$3, toDisplayString($props.client.status === "suspended" ? "Activate" : "Suspend"), 1), createBaseVNode("p", _hoisted_54$2, toDisplayString($props.client.status === "suspended" ? "Reactivate account" : "Temporarily disable"), 1)]),
				createBaseVNode("button", {
					onClick: _cache[5] || (_cache[5] = (...args) => $setup.forceLogout && $setup.forceLogout(...args)),
					class: "p-2.5 bg-red-50 dark:bg-red-500/10 hover:bg-red-100 dark:hover:bg-red-500/20 rounded-lg text-left transition-colors"
				}, [..._cache[57] || (_cache[57] = [createBaseVNode("p", { class: "text-xs font-medium text-red-700 dark:text-red-400" }, "Force Logout", -1), createBaseVNode("p", { class: "text-[10px] text-red-600 dark:text-red-500 mt-0.5" }, "End all sessions", -1)])])
			])])])) : createCommentVNode("", true)])
		]),
		$setup.showBalanceModal ? (openBlock(), createElementBlock("div", {
			key: 0,
			class: "fixed inset-0 bg-black/60 backdrop-blur-sm z-[60] flex items-center justify-center p-4",
			onClick: _cache[10] || (_cache[10] = withModifiers(($event) => $setup.showBalanceModal = false, ["self"]))
		}, [createBaseVNode("div", _hoisted_55$1, [
			createBaseVNode("div", _hoisted_56, [_cache[60] || (_cache[60] = createBaseVNode("div", { class: "w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-500/20 flex items-center justify-center" }, [createBaseVNode("svg", {
				class: "w-5 h-5 text-blue-600 dark:text-blue-400",
				fill: "none",
				stroke: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
			})])], -1)), createBaseVNode("div", null, [_cache[59] || (_cache[59] = createBaseVNode("h3", { class: "text-sm font-semibold text-slate-900 dark:text-white" }, "Adjust Balance", -1)), createBaseVNode("p", _hoisted_57, "Current: KSh " + toDisplayString($setup.formatNumber($props.client.balance)), 1)])]),
			createBaseVNode("div", _hoisted_58, [createBaseVNode("div", null, [_cache[61] || (_cache[61] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Amount", -1)), withDirectives(createBaseVNode("input", {
				"onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => $setup.balanceAmount = $event),
				type: "number",
				placeholder: "Enter amount (+ or -)",
				class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
			}, null, 512), [[vModelText, $setup.balanceAmount]])]), createBaseVNode("div", null, [_cache[62] || (_cache[62] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Reason", -1)), withDirectives(createBaseVNode("input", {
				"onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => $setup.balanceReason = $event),
				type: "text",
				placeholder: "Enter reason",
				class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
			}, null, 512), [[vModelText, $setup.balanceReason]])])]),
			createBaseVNode("div", _hoisted_59, [createBaseVNode("button", {
				onClick: _cache[8] || (_cache[8] = ($event) => $setup.showBalanceModal = false),
				class: "flex-1 px-3 py-2 text-xs font-medium bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg transition-colors"
			}, "Cancel"), createBaseVNode("button", {
				onClick: _cache[9] || (_cache[9] = (...args) => $setup.adjustBalance && $setup.adjustBalance(...args)),
				class: "flex-1 px-3 py-2 text-xs font-medium bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
			}, "Confirm")])
		])])) : createCommentVNode("", true),
		$setup.showPointsModal ? (openBlock(), createElementBlock("div", {
			key: 1,
			class: "fixed inset-0 bg-black/60 backdrop-blur-sm z-[60] flex items-center justify-center p-4",
			onClick: _cache[15] || (_cache[15] = withModifiers(($event) => $setup.showPointsModal = false, ["self"]))
		}, [createBaseVNode("div", _hoisted_60, [
			createBaseVNode("div", _hoisted_61, [_cache[64] || (_cache[64] = createBaseVNode("div", { class: "w-10 h-10 rounded-full bg-purple-100 dark:bg-purple-500/20 flex items-center justify-center" }, [createBaseVNode("svg", {
				class: "w-5 h-5 text-purple-600 dark:text-purple-400",
				fill: "none",
				stroke: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
			})])], -1)), createBaseVNode("div", null, [_cache[63] || (_cache[63] = createBaseVNode("h3", { class: "text-sm font-semibold text-slate-900 dark:text-white" }, "Award Points", -1)), createBaseVNode("p", _hoisted_62, "Current: " + toDisplayString($props.client.reward_points) + " points", 1)])]),
			createBaseVNode("div", _hoisted_63, [createBaseVNode("div", null, [_cache[65] || (_cache[65] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Points", -1)), withDirectives(createBaseVNode("input", {
				"onUpdate:modelValue": _cache[11] || (_cache[11] = ($event) => $setup.pointsAmount = $event),
				type: "number",
				placeholder: "Enter points",
				class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
			}, null, 512), [[vModelText, $setup.pointsAmount]])]), createBaseVNode("div", null, [_cache[66] || (_cache[66] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Description", -1)), withDirectives(createBaseVNode("input", {
				"onUpdate:modelValue": _cache[12] || (_cache[12] = ($event) => $setup.pointsReason = $event),
				type: "text",
				placeholder: "Enter description",
				class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
			}, null, 512), [[vModelText, $setup.pointsReason]])])]),
			createBaseVNode("div", _hoisted_64, [createBaseVNode("button", {
				onClick: _cache[13] || (_cache[13] = ($event) => $setup.showPointsModal = false),
				class: "flex-1 px-3 py-2 text-xs font-medium bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg transition-colors"
			}, "Cancel"), createBaseVNode("button", {
				onClick: _cache[14] || (_cache[14] = (...args) => $setup.awardPoints && $setup.awardPoints(...args)),
				class: "flex-1 px-3 py-2 text-xs font-medium bg-purple-500 hover:bg-purple-600 text-white rounded-lg transition-colors"
			}, "Award")])
		])])) : createCommentVNode("", true),
		createVNode(_component_ConfirmDialog, {
			show: $setup.confirmDialog.show,
			type: $setup.confirmDialog.type,
			title: $setup.confirmDialog.title,
			message: $setup.confirmDialog.message,
			confirmText: $setup.confirmDialog.confirmText,
			onConfirm: $setup.confirmDialog.onConfirm,
			onCancel: _cache[16] || (_cache[16] = ($event) => $setup.confirmDialog.show = false)
		}, null, 8, [
			"show",
			"type",
			"title",
			"message",
			"confirmText",
			"onConfirm"
		])
	])) : createCommentVNode("", true);
}
var _sfc_main$20 = {
	name: "Clients",
	components: {
		ModernMetricCard: MetricCard_default,
		ClientDetailModal: /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$21, [["render", _sfc_render$21]])
	},
	setup() {
		const { loading, error, makeRequest } = useApi();
		const clients = ref([]);
		const stats = ref({
			total_clients: 0,
			active_clients: 0,
			premium_clients: 0,
			new_clients_7d: 0,
			total_balance: 0
		});
		const searchTerm = ref("");
		const statusFilter = ref("");
		const tierFilter = ref("");
		const showAddModal = ref(false);
		const showEditModal = ref(false);
		const showDetailModal = ref(false);
		const selectedClient = ref(null);
		const formData = ref({
			username: "",
			email: "",
			phone_number: "",
			display_name: "",
			account_tier: "basic",
			status: "active",
			balance: 0,
			credit_limit: 0
		});
		const filteredClients = computed(() => {
			let result = clients.value;
			if (searchTerm.value) {
				const term = searchTerm.value.toLowerCase();
				result = result.filter((c) => c.user_username?.toLowerCase().includes(term) || c.phone_number?.includes(term) || c.account?.toLowerCase().includes(term));
			}
			if (statusFilter.value) result = result.filter((c) => c.status === statusFilter.value);
			if (tierFilter.value) result = result.filter((c) => c.account_tier === tierFilter.value);
			return result;
		});
		const fetchClients = async () => {
			try {
				const data = await makeRequest("get", "suapi/clients/");
				clients.value = data.results || data;
			} catch (err) {
				console.error("Error:", err);
			}
		};
		const fetchStats = async () => {
			try {
				stats.value = await makeRequest("get", "suapi/clients/stats/") || stats.value;
			} catch (err) {
				console.error("Error:", err);
			}
		};
		const refreshData = () => Promise.all([fetchClients(), fetchStats()]);
		const viewClient = (client) => {
			selectedClient.value = client;
			showDetailModal.value = true;
		};
		const editClient = (client) => {
			selectedClient.value = client;
			formData.value = {
				username: client.user_username,
				email: client.user_email || "",
				phone_number: client.phone_number || "",
				display_name: client.display_name || "",
				account_tier: client.account_tier,
				status: client.status,
				balance: client.balance,
				credit_limit: client.credit_limit
			};
			showEditModal.value = true;
		};
		const deleteClient = async (client) => {
			if (!confirm(`Delete client ${client.user_username}? This action cannot be undone.`)) return;
			try {
				await makeRequest("delete", `suapi/clients/${client.id}/`);
				await refreshData();
			} catch (err) {
				console.error("Error deleting client:", err);
				alert("Failed to delete client");
			}
		};
		const saveClient = async () => {
			try {
				if (showEditModal.value) await makeRequest("patch", `suapi/clients/${selectedClient.value.id}/`, formData.value);
				else await makeRequest("post", "suapi/clients/", formData.value);
				closeFormModal();
				await refreshData();
			} catch (err) {
				console.error("Error saving client:", err);
				alert("Failed to save client");
			}
		};
		const closeFormModal = () => {
			showAddModal.value = false;
			showEditModal.value = false;
			formData.value = {
				username: "",
				email: "",
				phone_number: "",
				display_name: "",
				account_tier: "basic",
				status: "active",
				balance: 0,
				credit_limit: 0
			};
		};
		const getInitials = (name) => {
			if (!name) return "?";
			return name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2);
		};
		const getTierBadge = (tier) => {
			const badges = {
				"basic": "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300",
				"premium": "bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400",
				"business": "bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400",
				"enterprise": "bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400"
			};
			return badges[tier] || badges.basic;
		};
		const getStatusBadge = (status) => {
			const badges = {
				"active": "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400",
				"inactive": "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400",
				"suspended": "bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400",
				"banned": "bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400"
			};
			return badges[status] || badges.inactive;
		};
		const formatNumber = (num) => {
			return new Intl.NumberFormat().format(num || 0);
		};
		const formatDate = (date) => {
			if (!date) return "N/A";
			return new Date(date).toLocaleDateString();
		};
		const handleImageError = (event) => {
			event.target.parentElement.innerHTML = `
        <svg class="w-4 h-4 text-slate-400 dark:text-slate-500" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
        </svg>
      `;
		};
		onMounted(refreshData);
		return {
			loading,
			error,
			clients,
			stats,
			searchTerm,
			statusFilter,
			tierFilter,
			filteredClients,
			fetchClients,
			refreshData,
			showAddModal,
			showEditModal,
			showDetailModal,
			selectedClient,
			formData,
			viewClient,
			editClient,
			deleteClient,
			saveClient,
			closeFormModal,
			getInitials,
			getTierBadge,
			getStatusBadge,
			formatNumber,
			formatDate,
			handleImageError
		};
	}
};
var _hoisted_1$20 = { class: "space-y-4 animate-fade-in" };
var _hoisted_2$20 = { class: "flex items-center justify-between" };
var _hoisted_3$20 = { class: "flex items-center gap-2" };
var _hoisted_4$20 = {
	key: 0,
	class: "bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-lg p-4"
};
var _hoisted_5$20 = { class: "flex items-center justify-between" };
var _hoisted_6$20 = { class: "flex items-center gap-3" };
var _hoisted_7$20 = { class: "text-xs text-rose-600 dark:text-rose-500 mt-1" };
var _hoisted_8$20 = { class: "grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 animate-slide-up" };
var _hoisted_9$18 = {
	class: "space-y-3 animate-slide-up",
	style: { "animation-delay": "0.1s" }
};
var _hoisted_10$17 = { class: "flex items-center gap-2" };
var _hoisted_11$16 = { class: "flex-1" };
var _hoisted_12$16 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden" };
var _hoisted_13$16 = { class: "overflow-x-auto" };
var _hoisted_14$16 = { class: "w-full" };
var _hoisted_15$16 = { class: "divide-y divide-slate-200 dark:divide-slate-700" };
var _hoisted_16$16 = ["onClick"];
var _hoisted_17$16 = { class: "px-3 py-2" };
var _hoisted_18$16 = { class: "flex items-center gap-2" };
var _hoisted_19$15 = {
	key: 0,
	class: "w-7 h-7 rounded-full overflow-hidden flex-shrink-0"
};
var _hoisted_20$15 = ["src"];
var _hoisted_21$15 = {
	key: 1,
	class: "w-7 h-7 rounded-full bg-slate-100 dark:bg-slate-700 flex items-center justify-center flex-shrink-0"
};
var _hoisted_22$15 = { class: "text-xs font-medium text-slate-900 dark:text-white" };
var _hoisted_23$15 = { class: "text-[10px] text-slate-500 dark:text-slate-400" };
var _hoisted_24$15 = { class: "px-3 py-2" };
var _hoisted_25$15 = { class: "text-xs text-slate-900 dark:text-white" };
var _hoisted_26$15 = { class: "text-[10px] text-slate-500 dark:text-slate-400" };
var _hoisted_27$14 = { class: "px-3 py-2" };
var _hoisted_28$14 = { class: "px-3 py-2" };
var _hoisted_29$14 = { class: "text-xs font-semibold text-slate-900 dark:text-white" };
var _hoisted_30$14 = { class: "px-3 py-2" };
var _hoisted_31$14 = { class: "flex items-center gap-1" };
var _hoisted_32$14 = { class: "text-xs text-slate-900 dark:text-white" };
var _hoisted_33$14 = { class: "px-3 py-2" };
var _hoisted_34$14 = { class: "px-3 py-2 text-xs text-slate-600 dark:text-slate-400" };
var _hoisted_35$14 = { class: "px-3 py-2 text-right" };
var _hoisted_36$14 = { class: "flex items-center justify-end gap-0.5" };
var _hoisted_37$14 = ["onClick"];
var _hoisted_38$14 = ["onClick"];
var _hoisted_39$14 = ["onClick"];
var _hoisted_40$14 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden" };
var _hoisted_41$13 = { class: "flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700" };
var _hoisted_42$11 = { class: "text-xl font-semibold text-slate-900 dark:text-white" };
var _hoisted_43$10 = { class: "p-6 overflow-y-auto max-h-[calc(90vh-140px)]" };
var _hoisted_44$10 = { class: "grid grid-cols-2 gap-4" };
var _hoisted_45$7 = ["disabled"];
var _hoisted_46$7 = { class: "flex items-center justify-end gap-2 p-6 border-t border-slate-200 dark:border-slate-700" };
function _sfc_render$20(_ctx, _cache, $props, $setup, $data, $options) {
	const _component_ModernMetricCard = resolveComponent("ModernMetricCard");
	const _component_ClientDetailModal = resolveComponent("ClientDetailModal");
	return openBlock(), createElementBlock("div", _hoisted_1$20, [
		createBaseVNode("div", _hoisted_2$20, [_cache[22] || (_cache[22] = createBaseVNode("div", null, [createBaseVNode("h1", { class: "text-lg font-semibold text-slate-900 dark:text-white" }, "Clients"), createBaseVNode("p", { class: "text-xs text-slate-500 dark:text-slate-400 mt-0.5" }, "Manage client accounts")], -1)), createBaseVNode("div", _hoisted_3$20, [createBaseVNode("button", {
			onClick: _cache[0] || (_cache[0] = ($event) => $setup.showAddModal = true),
			class: "px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white text-xs rounded-lg transition-colors flex items-center gap-1.5"
		}, [..._cache[20] || (_cache[20] = [createBaseVNode("svg", {
			class: "w-3.5 h-3.5",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M12 4v16m8-8H4"
		})], -1), createTextVNode(" Add Client ", -1)])]), createBaseVNode("button", {
			onClick: _cache[1] || (_cache[1] = (...args) => $setup.refreshData && $setup.refreshData(...args)),
			class: normalizeClass(["p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors", { "animate-spin": $setup.loading }])
		}, [..._cache[21] || (_cache[21] = [createBaseVNode("svg", {
			class: "w-4 h-4 text-slate-600 dark:text-slate-400",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
		})], -1)])], 2)])]),
		$setup.error ? (openBlock(), createElementBlock("div", _hoisted_4$20, [createBaseVNode("div", _hoisted_5$20, [createBaseVNode("div", _hoisted_6$20, [_cache[24] || (_cache[24] = createBaseVNode("svg", {
			class: "w-5 h-5 text-rose-600 dark:text-rose-400",
			fill: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" })], -1)), createBaseVNode("div", null, [_cache[23] || (_cache[23] = createBaseVNode("h3", { class: "text-sm font-medium text-rose-800 dark:text-rose-400" }, "Failed to load clients", -1)), createBaseVNode("p", _hoisted_7$20, toDisplayString($setup.error), 1)])]), createBaseVNode("button", {
			onClick: _cache[2] || (_cache[2] = (...args) => $setup.fetchClients && $setup.fetchClients(...args)),
			class: "px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm"
		}, "Retry")])])) : createCommentVNode("", true),
		createBaseVNode("div", _hoisted_8$20, [
			createVNode(_component_ModernMetricCard, {
				title: "Total Clients",
				value: $setup.stats.total_clients,
				color: "blue",
				trend: $setup.stats.total_clients_trend?.direction,
				trendValue: $setup.stats.total_clients_trend?.value
			}, {
				default: withCtx(() => [..._cache[25] || (_cache[25] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z" })], -1)])]),
				_: 1
			}, 8, [
				"value",
				"trend",
				"trendValue"
			]),
			createVNode(_component_ModernMetricCard, {
				title: "Total Balance",
				value: "KSh " + $setup.formatNumber($setup.stats.total_balance),
				color: "emerald",
				trend: "stable",
				trendValue: "0%"
			}, {
				default: withCtx(() => [..._cache[26] || (_cache[26] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Active",
				value: $setup.stats.active_clients,
				color: "cyan",
				trend: $setup.stats.active_clients_trend?.direction,
				trendValue: $setup.stats.active_clients_trend?.value,
				class: "col-span-2 md:col-span-1"
			}, {
				default: withCtx(() => [..._cache[27] || (_cache[27] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" })], -1)])]),
				_: 1
			}, 8, [
				"value",
				"trend",
				"trendValue"
			]),
			createVNode(_component_ModernMetricCard, {
				title: "Premium",
				value: $setup.stats.premium_clients,
				color: "purple",
				trend: $setup.stats.premium_clients_trend?.direction,
				trendValue: $setup.stats.premium_clients_trend?.value
			}, {
				default: withCtx(() => [..._cache[28] || (_cache[28] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" })], -1)])]),
				_: 1
			}, 8, [
				"value",
				"trend",
				"trendValue"
			]),
			createVNode(_component_ModernMetricCard, {
				title: "New (7d)",
				value: $setup.stats.new_clients_7d,
				color: "amber",
				trend: $setup.stats.new_clients_7d_trend?.direction,
				trendValue: $setup.stats.new_clients_7d_trend?.value
			}, {
				default: withCtx(() => [..._cache[29] || (_cache[29] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" })], -1)])]),
				_: 1
			}, 8, [
				"value",
				"trend",
				"trendValue"
			])
		]),
		createBaseVNode("div", _hoisted_9$18, [createBaseVNode("div", _hoisted_10$17, [
			createBaseVNode("div", _hoisted_11$16, [withDirectives(createBaseVNode("input", {
				"onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => $setup.searchTerm = $event),
				type: "text",
				placeholder: "Search by username, phone, or account...",
				class: "w-full px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs"
			}, null, 512), [[vModelText, $setup.searchTerm]])]),
			withDirectives(createBaseVNode("select", {
				"onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => $setup.statusFilter = $event),
				class: "px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs"
			}, [..._cache[30] || (_cache[30] = [
				createBaseVNode("option", { value: "" }, "All Status", -1),
				createBaseVNode("option", { value: "active" }, "Active", -1),
				createBaseVNode("option", { value: "inactive" }, "Inactive", -1),
				createBaseVNode("option", { value: "suspended" }, "Suspended", -1)
			])], 512), [[vModelSelect, $setup.statusFilter]]),
			withDirectives(createBaseVNode("select", {
				"onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => $setup.tierFilter = $event),
				class: "px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs"
			}, [..._cache[31] || (_cache[31] = [createStaticVNode("<option value=\"\" data-v-9387a2c9>All Tiers</option><option value=\"basic\" data-v-9387a2c9>Basic</option><option value=\"premium\" data-v-9387a2c9>Premium</option><option value=\"business\" data-v-9387a2c9>Business</option><option value=\"enterprise\" data-v-9387a2c9>Enterprise</option>", 5)])], 512), [[vModelSelect, $setup.tierFilter]])
		]), createBaseVNode("div", _hoisted_12$16, [createBaseVNode("div", _hoisted_13$16, [createBaseVNode("table", _hoisted_14$16, [_cache[37] || (_cache[37] = createBaseVNode("thead", { class: "bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700" }, [createBaseVNode("tr", null, [
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Client"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Contact"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Tier"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Balance"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Points"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Status"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Joined"),
			createBaseVNode("th", { class: "px-3 py-2 text-right text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Actions")
		])], -1)), createBaseVNode("tbody", _hoisted_15$16, [(openBlock(true), createElementBlock(Fragment, null, renderList($setup.filteredClients, (client) => {
			return openBlock(), createElementBlock("tr", {
				key: client.id,
				onClick: ($event) => $setup.viewClient(client),
				class: "hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer"
			}, [
				createBaseVNode("td", _hoisted_17$16, [createBaseVNode("div", _hoisted_18$16, [client.profile_image ? (openBlock(), createElementBlock("div", _hoisted_19$15, [createBaseVNode("img", {
					src: client.profile_image,
					alt: "Profile",
					class: "w-full h-full object-cover",
					onError: _cache[6] || (_cache[6] = (...args) => $setup.handleImageError && $setup.handleImageError(...args))
				}, null, 40, _hoisted_20$15)])) : (openBlock(), createElementBlock("div", _hoisted_21$15, [..._cache[32] || (_cache[32] = [createBaseVNode("svg", {
					class: "w-4 h-4 text-slate-400 dark:text-slate-500",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" })], -1)])])), createBaseVNode("div", null, [createBaseVNode("p", _hoisted_22$15, toDisplayString(client.user_username), 1), createBaseVNode("p", _hoisted_23$15, toDisplayString(client.account), 1)])])]),
				createBaseVNode("td", _hoisted_24$15, [createBaseVNode("p", _hoisted_25$15, toDisplayString(client.phone_number || "N/A"), 1), createBaseVNode("p", _hoisted_26$15, toDisplayString(client.user_email || "No email"), 1)]),
				createBaseVNode("td", _hoisted_27$14, [createBaseVNode("span", { class: normalizeClass(["px-1.5 py-0.5 text-[10px] font-medium rounded-full", $setup.getTierBadge(client.account_tier)]) }, toDisplayString(client.account_tier), 3)]),
				createBaseVNode("td", _hoisted_28$14, [createBaseVNode("p", _hoisted_29$14, "KSh " + toDisplayString($setup.formatNumber(client.balance)), 1)]),
				createBaseVNode("td", _hoisted_30$14, [createBaseVNode("div", _hoisted_31$14, [_cache[33] || (_cache[33] = createBaseVNode("svg", {
					class: "w-3 h-3 text-amber-500",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" })], -1)), createBaseVNode("span", _hoisted_32$14, toDisplayString(client.reward_points), 1)])]),
				createBaseVNode("td", _hoisted_33$14, [createBaseVNode("span", { class: normalizeClass(["px-1.5 py-0.5 text-[10px] font-medium rounded-full", $setup.getStatusBadge(client.status)]) }, toDisplayString(client.status), 3)]),
				createBaseVNode("td", _hoisted_34$14, toDisplayString($setup.formatDate(client.created_at)), 1),
				createBaseVNode("td", _hoisted_35$14, [createBaseVNode("div", _hoisted_36$14, [
					createBaseVNode("button", {
						onClick: withModifiers(($event) => $setup.viewClient(client), ["stop"]),
						class: "p-1 hover:bg-slate-100 dark:hover:bg-slate-600 rounded transition-colors",
						title: "View"
					}, [..._cache[34] || (_cache[34] = [createBaseVNode("svg", {
						class: "w-3.5 h-3.5 text-slate-600 dark:text-slate-400",
						fill: "none",
						stroke: "currentColor",
						viewBox: "0 0 24 24"
					}, [createBaseVNode("path", {
						"stroke-linecap": "round",
						"stroke-linejoin": "round",
						"stroke-width": "2",
						d: "M15 12a3 3 0 11-6 0 3 3 0 016 0z"
					}), createBaseVNode("path", {
						"stroke-linecap": "round",
						"stroke-linejoin": "round",
						"stroke-width": "2",
						d: "M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
					})], -1)])], 8, _hoisted_37$14),
					createBaseVNode("button", {
						onClick: withModifiers(($event) => $setup.editClient(client), ["stop"]),
						class: "p-1 hover:bg-blue-100 dark:hover:bg-blue-600 rounded transition-colors",
						title: "Edit"
					}, [..._cache[35] || (_cache[35] = [createBaseVNode("svg", {
						class: "w-3.5 h-3.5 text-blue-600 dark:text-blue-400",
						fill: "none",
						stroke: "currentColor",
						viewBox: "0 0 24 24"
					}, [createBaseVNode("path", {
						"stroke-linecap": "round",
						"stroke-linejoin": "round",
						"stroke-width": "2",
						d: "M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
					})], -1)])], 8, _hoisted_38$14),
					createBaseVNode("button", {
						onClick: withModifiers(($event) => $setup.deleteClient(client), ["stop"]),
						class: "p-1 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors",
						title: "Delete"
					}, [..._cache[36] || (_cache[36] = [createBaseVNode("svg", {
						class: "w-3.5 h-3.5 text-red-600 dark:text-red-400",
						fill: "none",
						stroke: "currentColor",
						viewBox: "0 0 24 24"
					}, [createBaseVNode("path", {
						"stroke-linecap": "round",
						"stroke-linejoin": "round",
						"stroke-width": "2",
						d: "M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
					})], -1)])], 8, _hoisted_39$14)
				])])
			], 8, _hoisted_16$16);
		}), 128))])])])])]),
		createVNode(_component_ClientDetailModal, {
			show: $setup.showDetailModal,
			client: $setup.selectedClient,
			onClose: _cache[7] || (_cache[7] = ($event) => $setup.showDetailModal = false),
			onRefresh: $setup.refreshData
		}, null, 8, [
			"show",
			"client",
			"onRefresh"
		]),
		$setup.showAddModal || $setup.showEditModal ? (openBlock(), createElementBlock("div", {
			key: 1,
			class: "fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4",
			onClick: _cache[19] || (_cache[19] = withModifiers((...args) => $setup.closeFormModal && $setup.closeFormModal(...args), ["self"]))
		}, [createBaseVNode("div", _hoisted_40$14, [
			createBaseVNode("div", _hoisted_41$13, [createBaseVNode("h2", _hoisted_42$11, toDisplayString($setup.showEditModal ? "Edit Client" : "Add New Client"), 1), createBaseVNode("button", {
				onClick: _cache[8] || (_cache[8] = (...args) => $setup.closeFormModal && $setup.closeFormModal(...args)),
				class: "p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
			}, [..._cache[38] || (_cache[38] = [createBaseVNode("svg", {
				class: "w-5 h-5",
				fill: "none",
				stroke: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M6 18L18 6M6 6l12 12"
			})], -1)])])]),
			createBaseVNode("div", _hoisted_43$10, [createBaseVNode("div", _hoisted_44$10, [
				createBaseVNode("div", null, [_cache[39] || (_cache[39] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Username", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[9] || (_cache[9] = ($event) => $setup.formData.username = $event),
					type: "text",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm",
					disabled: $setup.showEditModal
				}, null, 8, _hoisted_45$7), [[vModelText, $setup.formData.username]])]),
				createBaseVNode("div", null, [_cache[40] || (_cache[40] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Email", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[10] || (_cache[10] = ($event) => $setup.formData.email = $event),
					type: "email",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm"
				}, null, 512), [[vModelText, $setup.formData.email]])]),
				createBaseVNode("div", null, [_cache[41] || (_cache[41] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Phone Number", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[11] || (_cache[11] = ($event) => $setup.formData.phone_number = $event),
					type: "text",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm"
				}, null, 512), [[vModelText, $setup.formData.phone_number]])]),
				createBaseVNode("div", null, [_cache[42] || (_cache[42] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Display Name", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[12] || (_cache[12] = ($event) => $setup.formData.display_name = $event),
					type: "text",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm"
				}, null, 512), [[vModelText, $setup.formData.display_name]])]),
				createBaseVNode("div", null, [_cache[44] || (_cache[44] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Account Tier", -1)), withDirectives(createBaseVNode("select", {
					"onUpdate:modelValue": _cache[13] || (_cache[13] = ($event) => $setup.formData.account_tier = $event),
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm"
				}, [..._cache[43] || (_cache[43] = [
					createBaseVNode("option", { value: "basic" }, "Basic", -1),
					createBaseVNode("option", { value: "premium" }, "Premium", -1),
					createBaseVNode("option", { value: "business" }, "Business", -1),
					createBaseVNode("option", { value: "enterprise" }, "Enterprise", -1)
				])], 512), [[vModelSelect, $setup.formData.account_tier]])]),
				createBaseVNode("div", null, [_cache[46] || (_cache[46] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Status", -1)), withDirectives(createBaseVNode("select", {
					"onUpdate:modelValue": _cache[14] || (_cache[14] = ($event) => $setup.formData.status = $event),
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm"
				}, [..._cache[45] || (_cache[45] = [
					createBaseVNode("option", { value: "active" }, "Active", -1),
					createBaseVNode("option", { value: "inactive" }, "Inactive", -1),
					createBaseVNode("option", { value: "suspended" }, "Suspended", -1)
				])], 512), [[vModelSelect, $setup.formData.status]])]),
				createBaseVNode("div", null, [_cache[47] || (_cache[47] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Balance", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[15] || (_cache[15] = ($event) => $setup.formData.balance = $event),
					type: "number",
					step: "0.01",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm"
				}, null, 512), [[vModelText, $setup.formData.balance]])]),
				createBaseVNode("div", null, [_cache[48] || (_cache[48] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Credit Limit", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[16] || (_cache[16] = ($event) => $setup.formData.credit_limit = $event),
					type: "number",
					step: "0.01",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-sm"
				}, null, 512), [[vModelText, $setup.formData.credit_limit]])])
			])]),
			createBaseVNode("div", _hoisted_46$7, [createBaseVNode("button", {
				onClick: _cache[17] || (_cache[17] = (...args) => $setup.closeFormModal && $setup.closeFormModal(...args)),
				class: "px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg text-sm"
			}, "Cancel"), createBaseVNode("button", {
				onClick: _cache[18] || (_cache[18] = (...args) => $setup.saveClient && $setup.saveClient(...args)),
				class: "px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm"
			}, toDisplayString($setup.showEditModal ? "Update" : "Create"), 1)])
		])])) : createCommentVNode("", true)
	]);
}
var Clients_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$20, [["render", _sfc_render$20], ["__scopeId", "data-v-9387a2c9"]]);
var _sfc_main$19 = {
	name: "Users",
	components: {
		ModernMetricCard: MetricCard_default,
		ConfirmDialog: ConfirmDialog_default
	},
	setup() {
		const { loading, error, makeRequest } = useApi();
		const users = ref([]);
		const stats = ref({});
		const searchTerm = ref("");
		const statusFilter = ref("");
		const showFormModal = ref(false);
		const showDeleteModal = ref(false);
		const selectedUser = ref(null);
		const userToDelete = ref(null);
		const saveLoading = ref(false);
		const deleteLoading = ref(false);
		const formData = ref({
			username: "",
			email: "",
			first_name: "",
			last_name: "",
			password: "",
			confirm_password: "",
			is_active: true,
			is_staff: false,
			is_superuser: false
		});
		const filteredUsers = computed(() => {
			let result = users.value;
			if (searchTerm.value) {
				const term = searchTerm.value.toLowerCase();
				result = result.filter((u) => u.username?.toLowerCase().includes(term) || u.email?.toLowerCase().includes(term) || u.first_name?.toLowerCase().includes(term) || u.last_name?.toLowerCase().includes(term));
			}
			if (statusFilter.value) result = result.filter((u) => u.is_active === (statusFilter.value === "true"));
			return result;
		});
		const fetchUsers = async () => {
			try {
				const data = await makeRequest("get", "suapi/users/");
				users.value = data.results || data;
			} catch (err) {
				console.error("Error:", err);
			}
		};
		const fetchStats = async () => {
			try {
				stats.value = await makeRequest("get", "suapi/users/stats/");
			} catch (err) {
				console.error("Error:", err);
			}
		};
		const refreshData = () => Promise.all([fetchUsers(), fetchStats()]);
		const openAddModal = () => {
			selectedUser.value = null;
			formData.value = {
				username: "",
				email: "",
				first_name: "",
				last_name: "",
				password: "",
				confirm_password: "",
				is_active: true,
				is_staff: false,
				is_superuser: false
			};
			showFormModal.value = true;
		};
		const openEditModal = (user) => {
			selectedUser.value = user;
			formData.value = {
				username: user.username,
				email: user.email || "",
				first_name: user.first_name || "",
				last_name: user.last_name || "",
				password: "",
				is_active: user.is_active,
				is_staff: user.is_staff,
				is_superuser: user.is_superuser
			};
			showFormModal.value = true;
		};
		const closeFormModal = () => {
			showFormModal.value = false;
			selectedUser.value = null;
			formData.value = {
				username: "",
				email: "",
				first_name: "",
				last_name: "",
				password: "",
				confirm_password: "",
				is_active: true,
				is_staff: false,
				is_superuser: false
			};
		};
		const saveUser = async () => {
			if (!selectedUser.value?.id) {
				if (!formData.value.password) {
					alert("Password is required for new users");
					return;
				}
				if (formData.value.password !== formData.value.confirm_password) {
					alert("Passwords do not match");
					return;
				}
			}
			saveLoading.value = true;
			try {
				const payload = { ...formData.value };
				delete payload.confirm_password;
				if (!payload.password) delete payload.password;
				if (selectedUser.value?.id) await makeRequest("patch", `suapi/users/${selectedUser.value.id}/`, payload);
				else await makeRequest("post", "suapi/users/", payload);
				await refreshData();
				closeFormModal();
			} catch (err) {
				alert("Error: " + (err.response?.data?.error || err.message));
			} finally {
				saveLoading.value = false;
			}
		};
		const openDeleteModal = (user) => {
			userToDelete.value = user;
			showDeleteModal.value = true;
		};
		const closeDeleteModal = () => {
			showDeleteModal.value = false;
			userToDelete.value = null;
		};
		const confirmDelete = async () => {
			deleteLoading.value = true;
			try {
				await makeRequest("delete", `suapi/users/${userToDelete.value.id}/`);
				await refreshData();
				closeDeleteModal();
			} catch (err) {
				alert("Error: " + (err.response?.data?.error || err.message));
			} finally {
				deleteLoading.value = false;
			}
		};
		const getInitials = (name) => {
			if (!name) return "?";
			return name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2);
		};
		onMounted(refreshData);
		return {
			loading,
			error,
			users,
			stats,
			searchTerm,
			statusFilter,
			showFormModal,
			showDeleteModal,
			selectedUser,
			userToDelete,
			saveLoading,
			deleteLoading,
			formData,
			filteredUsers,
			fetchUsers,
			refreshData,
			openAddModal,
			openEditModal,
			closeFormModal,
			saveUser,
			openDeleteModal,
			closeDeleteModal,
			confirmDelete,
			getInitials
		};
	}
};
var _hoisted_1$19 = { class: "space-y-4 animate-fade-in" };
var _hoisted_2$19 = { class: "flex items-center justify-between" };
var _hoisted_3$19 = { class: "flex items-center gap-2" };
var _hoisted_4$19 = {
	key: 0,
	class: "bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-lg p-4"
};
var _hoisted_5$19 = { class: "flex items-center justify-between" };
var _hoisted_6$19 = { class: "flex items-center gap-3" };
var _hoisted_7$19 = { class: "text-xs text-rose-600 dark:text-rose-500 mt-1" };
var _hoisted_8$19 = { class: "grid grid-cols-2 md:grid-cols-4 gap-3 animate-slide-up" };
var _hoisted_9$17 = {
	class: "space-y-3 animate-slide-up",
	style: { "animation-delay": "0.1s" }
};
var _hoisted_10$16 = { class: "flex items-center gap-2" };
var _hoisted_11$15 = { class: "flex-1" };
var _hoisted_12$15 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden" };
var _hoisted_13$15 = { class: "overflow-x-auto" };
var _hoisted_14$15 = { class: "w-full" };
var _hoisted_15$15 = { class: "divide-y divide-slate-200 dark:divide-slate-700" };
var _hoisted_16$15 = ["onClick"];
var _hoisted_17$15 = { class: "px-3 py-2" };
var _hoisted_18$15 = { class: "flex items-center gap-2" };
var _hoisted_19$14 = { class: "w-7 h-7 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold" };
var _hoisted_20$14 = { class: "text-xs font-medium text-slate-900 dark:text-white" };
var _hoisted_21$14 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white" };
var _hoisted_22$14 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white" };
var _hoisted_23$14 = { class: "px-3 py-2" };
var _hoisted_24$14 = { class: "px-3 py-2" };
var _hoisted_25$14 = { class: "flex items-center gap-1" };
var _hoisted_26$14 = {
	key: 0,
	class: "text-xs text-amber-600 dark:text-amber-400"
};
var _hoisted_27$13 = {
	key: 1,
	class: "text-xs text-purple-600 dark:text-purple-400"
};
var _hoisted_28$13 = { class: "px-3 py-2 text-right" };
var _hoisted_29$13 = { class: "flex items-center justify-end gap-0.5" };
var _hoisted_30$13 = ["onClick"];
var _hoisted_31$13 = ["onClick"];
var _hoisted_32$13 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden" };
var _hoisted_33$13 = { class: "flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700" };
var _hoisted_34$13 = { class: "text-base font-semibold text-slate-900 dark:text-white" };
var _hoisted_35$13 = { class: "p-5 overflow-y-auto max-h-[calc(90vh-140px)]" };
var _hoisted_36$13 = { class: "grid grid-cols-2 gap-4" };
var _hoisted_37$13 = ["disabled"];
var _hoisted_38$13 = { class: "col-span-2" };
var _hoisted_39$13 = { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" };
var _hoisted_40$13 = ["placeholder", "required"];
var _hoisted_41$12 = {
	key: 0,
	class: "col-span-2"
};
var _hoisted_42$10 = { class: "col-span-2 space-y-2" };
var _hoisted_43$9 = { class: "flex items-center gap-2" };
var _hoisted_44$9 = { class: "flex items-center gap-2" };
var _hoisted_45$6 = { class: "flex items-center gap-2" };
var _hoisted_46$6 = { class: "flex items-center justify-end gap-2 p-5 border-t border-slate-200 dark:border-slate-700" };
var _hoisted_47$6 = ["disabled"];
function _sfc_render$19(_ctx, _cache, $props, $setup, $data, $options) {
	const _component_ModernMetricCard = resolveComponent("ModernMetricCard");
	const _component_ConfirmDialog = resolveComponent("ConfirmDialog");
	return openBlock(), createElementBlock("div", _hoisted_1$19, [
		createBaseVNode("div", _hoisted_2$19, [_cache[20] || (_cache[20] = createBaseVNode("div", null, [createBaseVNode("h1", { class: "text-lg font-semibold text-slate-900 dark:text-white" }, "Users"), createBaseVNode("p", { class: "text-xs text-slate-500 dark:text-slate-400 mt-0.5" }, "Manage Django user accounts")], -1)), createBaseVNode("div", _hoisted_3$19, [createBaseVNode("button", {
			onClick: _cache[0] || (_cache[0] = (...args) => $setup.openAddModal && $setup.openAddModal(...args)),
			class: "px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-xs flex items-center gap-1.5"
		}, [..._cache[18] || (_cache[18] = [createBaseVNode("svg", {
			class: "w-3.5 h-3.5",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M12 4v16m8-8H4"
		})], -1), createTextVNode(" Add User ", -1)])]), createBaseVNode("button", {
			onClick: _cache[1] || (_cache[1] = (...args) => $setup.refreshData && $setup.refreshData(...args)),
			class: normalizeClass(["p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors", { "animate-spin": $setup.loading }])
		}, [..._cache[19] || (_cache[19] = [createBaseVNode("svg", {
			class: "w-4 h-4 text-slate-600 dark:text-slate-400",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
		})], -1)])], 2)])]),
		$setup.error ? (openBlock(), createElementBlock("div", _hoisted_4$19, [createBaseVNode("div", _hoisted_5$19, [createBaseVNode("div", _hoisted_6$19, [_cache[22] || (_cache[22] = createBaseVNode("svg", {
			class: "w-5 h-5 text-rose-600 dark:text-rose-400",
			fill: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" })], -1)), createBaseVNode("div", null, [_cache[21] || (_cache[21] = createBaseVNode("h3", { class: "text-sm font-medium text-rose-800 dark:text-rose-400" }, "Failed to load users", -1)), createBaseVNode("p", _hoisted_7$19, toDisplayString($setup.error), 1)])]), createBaseVNode("button", {
			onClick: _cache[2] || (_cache[2] = (...args) => $setup.fetchUsers && $setup.fetchUsers(...args)),
			class: "px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm"
		}, "Retry")])])) : createCommentVNode("", true),
		createBaseVNode("div", _hoisted_8$19, [
			createVNode(_component_ModernMetricCard, {
				title: "Total Users",
				value: $setup.stats.total_users,
				color: "blue"
			}, {
				default: withCtx(() => [..._cache[23] || (_cache[23] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Active Users",
				value: $setup.stats.active_users,
				color: "emerald"
			}, {
				default: withCtx(() => [..._cache[24] || (_cache[24] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Staff Users",
				value: $setup.stats.staff_users,
				color: "purple",
				class: "col-span-2 md:col-span-1"
			}, {
				default: withCtx(() => [..._cache[25] || (_cache[25] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M20 6h-4V4c0-1.11-.89-2-2-2h-4c-1.11 0-2 .89-2 2v2H4c-1.11 0-1.99.89-1.99 2L2 19c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2zm-6 0h-4V4h4v2z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Superusers",
				value: $setup.stats.superusers,
				color: "amber"
			}, {
				default: withCtx(() => [..._cache[26] || (_cache[26] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" })], -1)])]),
				_: 1
			}, 8, ["value"])
		]),
		createBaseVNode("div", _hoisted_9$17, [createBaseVNode("div", _hoisted_10$16, [createBaseVNode("div", _hoisted_11$15, [withDirectives(createBaseVNode("input", {
			"onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => $setup.searchTerm = $event),
			type: "text",
			placeholder: "Search users...",
			class: "w-full px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs"
		}, null, 512), [[vModelText, $setup.searchTerm]])]), withDirectives(createBaseVNode("select", {
			"onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => $setup.statusFilter = $event),
			class: "px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs"
		}, [..._cache[27] || (_cache[27] = [
			createBaseVNode("option", { value: "" }, "All Status", -1),
			createBaseVNode("option", { value: "true" }, "Active", -1),
			createBaseVNode("option", { value: "false" }, "Inactive", -1)
		])], 512), [[vModelSelect, $setup.statusFilter]])]), createBaseVNode("div", _hoisted_12$15, [createBaseVNode("div", _hoisted_13$15, [createBaseVNode("table", _hoisted_14$15, [_cache[30] || (_cache[30] = createBaseVNode("thead", { class: "bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700" }, [createBaseVNode("tr", null, [
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "User"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Email"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Name"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Status"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Roles"),
			createBaseVNode("th", { class: "px-3 py-2 text-right text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Actions")
		])], -1)), createBaseVNode("tbody", _hoisted_15$15, [(openBlock(true), createElementBlock(Fragment, null, renderList($setup.filteredUsers, (user) => {
			return openBlock(), createElementBlock("tr", {
				key: user.id,
				onClick: ($event) => $setup.openEditModal(user),
				class: "hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer"
			}, [
				createBaseVNode("td", _hoisted_17$15, [createBaseVNode("div", _hoisted_18$15, [createBaseVNode("div", _hoisted_19$14, toDisplayString($setup.getInitials(user.username)), 1), createBaseVNode("p", _hoisted_20$14, toDisplayString(user.username), 1)])]),
				createBaseVNode("td", _hoisted_21$14, toDisplayString(user.email || "N/A"), 1),
				createBaseVNode("td", _hoisted_22$14, toDisplayString(user.first_name) + " " + toDisplayString(user.last_name), 1),
				createBaseVNode("td", _hoisted_23$14, [createBaseVNode("span", { class: normalizeClass(["px-1.5 py-0.5 text-[10px] font-medium rounded-full", user.is_active ? "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400" : "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400"]) }, toDisplayString(user.is_active ? "Active" : "Inactive"), 3)]),
				createBaseVNode("td", _hoisted_24$14, [createBaseVNode("div", _hoisted_25$14, [user.is_superuser ? (openBlock(), createElementBlock("span", _hoisted_26$14, "⭐")) : createCommentVNode("", true), user.is_staff ? (openBlock(), createElementBlock("span", _hoisted_27$13, "👔")) : createCommentVNode("", true)])]),
				createBaseVNode("td", _hoisted_28$13, [createBaseVNode("div", _hoisted_29$13, [createBaseVNode("button", {
					onClick: withModifiers(($event) => $setup.openEditModal(user), ["stop"]),
					class: "p-1 hover:bg-blue-100 dark:hover:bg-blue-600 rounded transition-colors",
					title: "Edit"
				}, [..._cache[28] || (_cache[28] = [createBaseVNode("svg", {
					class: "w-3.5 h-3.5 text-blue-600 dark:text-blue-400",
					fill: "none",
					stroke: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", {
					"stroke-linecap": "round",
					"stroke-linejoin": "round",
					"stroke-width": "2",
					d: "M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
				})], -1)])], 8, _hoisted_30$13), createBaseVNode("button", {
					onClick: withModifiers(($event) => $setup.openDeleteModal(user), ["stop"]),
					class: "p-1 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors",
					title: "Delete"
				}, [..._cache[29] || (_cache[29] = [createBaseVNode("svg", {
					class: "w-3.5 h-3.5 text-red-600 dark:text-red-400",
					fill: "none",
					stroke: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", {
					"stroke-linecap": "round",
					"stroke-linejoin": "round",
					"stroke-width": "2",
					d: "M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
				})], -1)])], 8, _hoisted_31$13)])])
			], 8, _hoisted_16$15);
		}), 128))])])])])]),
		$setup.showFormModal ? (openBlock(), createElementBlock("div", {
			key: 1,
			class: "fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4",
			onClick: _cache[17] || (_cache[17] = withModifiers((...args) => $setup.closeFormModal && $setup.closeFormModal(...args), ["self"]))
		}, [createBaseVNode("div", _hoisted_32$13, [
			createBaseVNode("div", _hoisted_33$13, [createBaseVNode("h2", _hoisted_34$13, toDisplayString($setup.selectedUser?.id ? "Edit User" : "Add User"), 1), createBaseVNode("button", {
				onClick: _cache[5] || (_cache[5] = (...args) => $setup.closeFormModal && $setup.closeFormModal(...args)),
				class: "p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
			}, [..._cache[31] || (_cache[31] = [createBaseVNode("svg", {
				class: "w-4 h-4",
				fill: "none",
				stroke: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M6 18L18 6M6 6l12 12"
			})], -1)])])]),
			createBaseVNode("div", _hoisted_35$13, [createBaseVNode("div", _hoisted_36$13, [
				createBaseVNode("div", null, [_cache[32] || (_cache[32] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Username", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => $setup.formData.username = $event),
					type: "text",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white",
					disabled: !!$setup.selectedUser?.id
				}, null, 8, _hoisted_37$13), [[vModelText, $setup.formData.username]])]),
				createBaseVNode("div", null, [_cache[33] || (_cache[33] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Email", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => $setup.formData.email = $event),
					type: "email",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.email]])]),
				createBaseVNode("div", null, [_cache[34] || (_cache[34] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "First Name", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[8] || (_cache[8] = ($event) => $setup.formData.first_name = $event),
					type: "text",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.first_name]])]),
				createBaseVNode("div", null, [_cache[35] || (_cache[35] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Last Name", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[9] || (_cache[9] = ($event) => $setup.formData.last_name = $event),
					type: "text",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.last_name]])]),
				createBaseVNode("div", _hoisted_38$13, [createBaseVNode("label", _hoisted_39$13, "Password " + toDisplayString($setup.selectedUser?.id ? "(leave blank to keep current)" : ""), 1), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[10] || (_cache[10] = ($event) => $setup.formData.password = $event),
					type: "password",
					placeholder: $setup.selectedUser?.id ? "Leave blank to keep current" : "Enter password",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white",
					required: !$setup.selectedUser?.id
				}, null, 8, _hoisted_40$13), [[vModelText, $setup.formData.password]])]),
				!$setup.selectedUser?.id ? (openBlock(), createElementBlock("div", _hoisted_41$12, [_cache[36] || (_cache[36] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Confirm Password", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[11] || (_cache[11] = ($event) => $setup.formData.confirm_password = $event),
					type: "password",
					placeholder: "Confirm password",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white",
					required: ""
				}, null, 512), [[vModelText, $setup.formData.confirm_password]])])) : createCommentVNode("", true),
				createBaseVNode("div", _hoisted_42$10, [
					createBaseVNode("label", _hoisted_43$9, [withDirectives(createBaseVNode("input", {
						"onUpdate:modelValue": _cache[12] || (_cache[12] = ($event) => $setup.formData.is_active = $event),
						type: "checkbox",
						class: "w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded"
					}, null, 512), [[vModelCheckbox, $setup.formData.is_active]]), _cache[37] || (_cache[37] = createBaseVNode("span", { class: "text-xs text-slate-700 dark:text-slate-300" }, "Active", -1))]),
					createBaseVNode("label", _hoisted_44$9, [withDirectives(createBaseVNode("input", {
						"onUpdate:modelValue": _cache[13] || (_cache[13] = ($event) => $setup.formData.is_staff = $event),
						type: "checkbox",
						class: "w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded"
					}, null, 512), [[vModelCheckbox, $setup.formData.is_staff]]), _cache[38] || (_cache[38] = createBaseVNode("span", { class: "text-xs text-slate-700 dark:text-slate-300" }, "Staff", -1))]),
					createBaseVNode("label", _hoisted_45$6, [withDirectives(createBaseVNode("input", {
						"onUpdate:modelValue": _cache[14] || (_cache[14] = ($event) => $setup.formData.is_superuser = $event),
						type: "checkbox",
						class: "w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded"
					}, null, 512), [[vModelCheckbox, $setup.formData.is_superuser]]), _cache[39] || (_cache[39] = createBaseVNode("span", { class: "text-xs text-slate-700 dark:text-slate-300" }, "Superuser", -1))])
				])
			])]),
			createBaseVNode("div", _hoisted_46$6, [createBaseVNode("button", {
				onClick: _cache[15] || (_cache[15] = (...args) => $setup.closeFormModal && $setup.closeFormModal(...args)),
				class: "px-3 py-2 text-xs bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg"
			}, "Cancel"), createBaseVNode("button", {
				onClick: _cache[16] || (_cache[16] = (...args) => $setup.saveUser && $setup.saveUser(...args)),
				disabled: $setup.saveLoading,
				class: normalizeClass(["px-3 py-2 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-lg", { "opacity-50": $setup.saveLoading }])
			}, toDisplayString($setup.saveLoading ? "Saving..." : $setup.selectedUser?.id ? "Update" : "Create"), 11, _hoisted_47$6)])
		])])) : createCommentVNode("", true),
		createVNode(_component_ConfirmDialog, {
			show: $setup.showDeleteModal,
			title: "Delete User",
			message: `Delete user ${$setup.userToDelete?.username}?`,
			type: "danger",
			onConfirm: $setup.confirmDelete,
			onCancel: $setup.closeDeleteModal
		}, null, 8, [
			"show",
			"message",
			"onConfirm",
			"onCancel"
		])
	]);
}
var Users_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$19, [["render", _sfc_render$19], ["__scopeId", "data-v-7d7629b6"]]);
var _sfc_main$18 = {
	name: "Devices",
	components: {
		ModernMetricCard: MetricCard_default,
		ConfirmDialog: ConfirmDialog_default
	},
	setup() {
		const { loading, error, makeRequest } = useApi();
		const devices = ref([]);
		const stats = ref({});
		const searchTerm = ref("");
		const statusFilter = ref("");
		const typeFilter = ref("");
		const showFormModal = ref(false);
		const showDeleteModal = ref(false);
		const selectedDevice = ref(null);
		const deviceToDelete = ref(null);
		const saveLoading = ref(false);
		const deleteLoading = ref(false);
		const formData = ref({
			mac_address: "",
			device_name: "",
			device_type: "phone",
			device_platform: "android",
			status: "active",
			is_trusted: false
		});
		const filteredDevices = computed(() => {
			let result = devices.value;
			if (searchTerm.value) {
				const term = searchTerm.value.toLowerCase();
				result = result.filter((d) => d.mac_address?.toLowerCase().includes(term) || d.device_name?.toLowerCase().includes(term) || d.user_account?.toLowerCase().includes(term));
			}
			if (statusFilter.value) result = result.filter((d) => d.status === statusFilter.value);
			if (typeFilter.value) result = result.filter((d) => d.device_type === typeFilter.value);
			return result;
		});
		const fetchDevices = async () => {
			try {
				const data = await makeRequest("get", "suapi/devices/");
				devices.value = data.results || data;
			} catch (err) {
				console.error("Error:", err);
			}
		};
		const fetchStats = async () => {
			try {
				stats.value = await makeRequest("get", "suapi/devices/stats/");
			} catch (err) {
				console.error("Error:", err);
			}
		};
		const refreshData = () => Promise.all([fetchDevices(), fetchStats()]);
		const openAddModal = () => {
			selectedDevice.value = null;
			formData.value = {
				mac_address: "",
				device_name: "",
				device_type: "phone",
				device_platform: "android",
				status: "active",
				is_trusted: false
			};
			showFormModal.value = true;
		};
		const openEditModal = (device) => {
			selectedDevice.value = device;
			formData.value = {
				mac_address: device.mac_address || "",
				device_name: device.device_name || "",
				device_type: device.device_type || "phone",
				device_platform: device.device_platform || "android",
				status: device.status || "active",
				is_trusted: device.is_trusted || false
			};
			showFormModal.value = true;
		};
		const closeFormModal = () => {
			showFormModal.value = false;
			selectedDevice.value = null;
			formData.value = {
				mac_address: "",
				device_name: "",
				device_type: "phone",
				device_platform: "android",
				status: "active",
				is_trusted: false
			};
		};
		const saveDevice = async () => {
			saveLoading.value = true;
			try {
				if (selectedDevice.value?.id) await makeRequest("patch", `suapi/devices/${selectedDevice.value.id}/`, formData.value);
				else await makeRequest("post", "suapi/devices/", formData.value);
				await refreshData();
				closeFormModal();
			} catch (err) {
				alert("Error: " + (err.response?.data?.error || err.message));
			} finally {
				saveLoading.value = false;
			}
		};
		const blockDevice = async (device) => {
			try {
				await makeRequest("post", `suapi/devices/${device.id}/block/`, { reason: "Admin action" });
				await refreshData();
			} catch (err) {
				alert("Error: " + (err.response?.data?.error || err.message));
			}
		};
		const unblockDevice = async (device) => {
			try {
				await makeRequest("post", `suapi/devices/${device.id}/unblock/`, { reason: "Admin action" });
				await refreshData();
			} catch (err) {
				alert("Error: " + (err.response?.data?.error || err.message));
			}
		};
		const openDeleteModal = (device) => {
			deviceToDelete.value = device;
			showDeleteModal.value = true;
		};
		const closeDeleteModal = () => {
			showDeleteModal.value = false;
			deviceToDelete.value = null;
		};
		const confirmDelete = async () => {
			deleteLoading.value = true;
			try {
				await makeRequest("delete", `suapi/devices/${deviceToDelete.value.id}/`);
				await refreshData();
				closeDeleteModal();
			} catch (err) {
				alert("Error: " + (err.response?.data?.error || err.message));
			} finally {
				deleteLoading.value = false;
			}
		};
		const getStatusBadge = (status) => {
			const badges = {
				"active": "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400",
				"inactive": "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400",
				"suspended": "bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400"
			};
			return badges[status] || badges.inactive;
		};
		onMounted(refreshData);
		return {
			loading,
			error,
			devices,
			stats,
			searchTerm,
			statusFilter,
			typeFilter,
			showFormModal,
			showDeleteModal,
			selectedDevice,
			deviceToDelete,
			saveLoading,
			deleteLoading,
			formData,
			filteredDevices,
			fetchDevices,
			refreshData,
			openAddModal,
			openEditModal,
			closeFormModal,
			saveDevice,
			blockDevice,
			unblockDevice,
			openDeleteModal,
			closeDeleteModal,
			confirmDelete,
			getStatusBadge
		};
	}
};
var _hoisted_1$18 = { class: "space-y-4 animate-fade-in" };
var _hoisted_2$18 = { class: "flex items-center justify-between" };
var _hoisted_3$18 = { class: "flex items-center gap-2" };
var _hoisted_4$18 = {
	key: 0,
	class: "bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-lg p-4"
};
var _hoisted_5$18 = { class: "flex items-center justify-between" };
var _hoisted_6$18 = { class: "flex items-center gap-3" };
var _hoisted_7$18 = { class: "text-xs text-rose-600 dark:text-rose-500 mt-1" };
var _hoisted_8$18 = { class: "grid grid-cols-2 md:grid-cols-4 gap-3 animate-slide-up" };
var _hoisted_9$16 = {
	class: "space-y-3 animate-slide-up",
	style: { "animation-delay": "0.1s" }
};
var _hoisted_10$15 = { class: "flex items-center gap-2" };
var _hoisted_11$14 = { class: "flex-1" };
var _hoisted_12$14 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden" };
var _hoisted_13$14 = { class: "overflow-x-auto" };
var _hoisted_14$14 = { class: "w-full" };
var _hoisted_15$14 = { class: "divide-y divide-slate-200 dark:divide-slate-700" };
var _hoisted_16$14 = ["onClick"];
var _hoisted_17$14 = { class: "px-3 py-2" };
var _hoisted_18$14 = { class: "flex items-center gap-2" };
var _hoisted_19$13 = { class: "text-xs font-medium text-slate-900 dark:text-white" };
var _hoisted_20$13 = { class: "text-[10px] text-slate-500 dark:text-slate-400" };
var _hoisted_21$13 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white" };
var _hoisted_22$13 = { class: "px-3 py-2" };
var _hoisted_23$13 = { class: "px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300" };
var _hoisted_24$13 = { class: "px-3 py-2" };
var _hoisted_25$13 = { class: "px-3 py-2" };
var _hoisted_26$13 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white" };
var _hoisted_27$12 = { class: "px-3 py-2 text-right" };
var _hoisted_28$12 = { class: "flex items-center justify-end gap-0.5" };
var _hoisted_29$12 = ["onClick"];
var _hoisted_30$12 = ["onClick"];
var _hoisted_31$12 = ["onClick"];
var _hoisted_32$12 = ["onClick"];
var _hoisted_33$12 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden" };
var _hoisted_34$12 = { class: "flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700" };
var _hoisted_35$12 = { class: "text-base font-semibold text-slate-900 dark:text-white" };
var _hoisted_36$12 = { class: "p-5 overflow-y-auto max-h-[calc(90vh-140px)]" };
var _hoisted_37$12 = { class: "grid grid-cols-2 gap-4" };
var _hoisted_38$12 = { class: "flex items-center" };
var _hoisted_39$12 = { class: "flex items-center gap-2 cursor-pointer" };
var _hoisted_40$12 = { class: "flex items-center justify-end gap-2 p-5 border-t border-slate-200 dark:border-slate-700" };
var _hoisted_41$11 = ["disabled"];
function _sfc_render$18(_ctx, _cache, $props, $setup, $data, $options) {
	const _component_ModernMetricCard = resolveComponent("ModernMetricCard");
	const _component_ConfirmDialog = resolveComponent("ConfirmDialog");
	return openBlock(), createElementBlock("div", _hoisted_1$18, [
		createBaseVNode("div", _hoisted_2$18, [_cache[18] || (_cache[18] = createBaseVNode("div", null, [createBaseVNode("h1", { class: "text-lg font-semibold text-slate-900 dark:text-white" }, "Devices"), createBaseVNode("p", { class: "text-xs text-slate-500 dark:text-slate-400 mt-0.5" }, "Monitor and manage user devices")], -1)), createBaseVNode("div", _hoisted_3$18, [createBaseVNode("button", {
			onClick: _cache[0] || (_cache[0] = (...args) => $setup.openAddModal && $setup.openAddModal(...args)),
			class: "px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-xs flex items-center gap-1.5"
		}, [..._cache[16] || (_cache[16] = [createBaseVNode("svg", {
			class: "w-3.5 h-3.5",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M12 4v16m8-8H4"
		})], -1), createTextVNode(" Add Device ", -1)])]), createBaseVNode("button", {
			onClick: _cache[1] || (_cache[1] = (...args) => $setup.refreshData && $setup.refreshData(...args)),
			class: normalizeClass(["p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors", { "animate-spin": $setup.loading }])
		}, [..._cache[17] || (_cache[17] = [createBaseVNode("svg", {
			class: "w-4 h-4 text-slate-600 dark:text-slate-400",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
		})], -1)])], 2)])]),
		$setup.error ? (openBlock(), createElementBlock("div", _hoisted_4$18, [createBaseVNode("div", _hoisted_5$18, [createBaseVNode("div", _hoisted_6$18, [_cache[20] || (_cache[20] = createBaseVNode("svg", {
			class: "w-5 h-5 text-rose-600 dark:text-rose-400",
			fill: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" })], -1)), createBaseVNode("div", null, [_cache[19] || (_cache[19] = createBaseVNode("h3", { class: "text-sm font-medium text-rose-800 dark:text-rose-400" }, "Failed to load devices", -1)), createBaseVNode("p", _hoisted_7$18, toDisplayString($setup.error), 1)])]), createBaseVNode("button", {
			onClick: _cache[2] || (_cache[2] = (...args) => $setup.fetchDevices && $setup.fetchDevices(...args)),
			class: "px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm"
		}, "Retry")])])) : createCommentVNode("", true),
		createBaseVNode("div", _hoisted_8$18, [
			createVNode(_component_ModernMetricCard, {
				title: "Total Devices",
				value: $setup.stats.total_devices,
				color: "blue"
			}, {
				default: withCtx(() => [..._cache[21] || (_cache[21] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M17 1.01L7 1c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-1.99-2-1.99zM17 19H7V5h10v14z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Active",
				value: $setup.stats.active_devices,
				color: "emerald"
			}, {
				default: withCtx(() => [..._cache[22] || (_cache[22] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Online",
				value: $setup.stats.online_devices,
				color: "cyan"
			}, {
				default: withCtx(() => [..._cache[23] || (_cache[23] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Trusted",
				value: $setup.stats.trusted_devices,
				color: "purple"
			}, {
				default: withCtx(() => [..._cache[24] || (_cache[24] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm-2 16l-4-4 1.41-1.41L10 14.17l6.59-6.59L18 9l-8 8z" })], -1)])]),
				_: 1
			}, 8, ["value"])
		]),
		createBaseVNode("div", _hoisted_9$16, [createBaseVNode("div", _hoisted_10$15, [
			createBaseVNode("div", _hoisted_11$14, [withDirectives(createBaseVNode("input", {
				"onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => $setup.searchTerm = $event),
				type: "text",
				placeholder: "Search devices...",
				class: "w-full px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs"
			}, null, 512), [[vModelText, $setup.searchTerm]])]),
			withDirectives(createBaseVNode("select", {
				"onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => $setup.statusFilter = $event),
				class: "px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs"
			}, [..._cache[25] || (_cache[25] = [
				createBaseVNode("option", { value: "" }, "All Status", -1),
				createBaseVNode("option", { value: "active" }, "Active", -1),
				createBaseVNode("option", { value: "inactive" }, "Inactive", -1),
				createBaseVNode("option", { value: "suspended" }, "Suspended", -1)
			])], 512), [[vModelSelect, $setup.statusFilter]]),
			withDirectives(createBaseVNode("select", {
				"onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => $setup.typeFilter = $event),
				class: "px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs"
			}, [..._cache[26] || (_cache[26] = [createStaticVNode("<option value=\"\" data-v-9b0b6231>All Types</option><option value=\"phone\" data-v-9b0b6231>Phone</option><option value=\"laptop\" data-v-9b0b6231>Laptop</option><option value=\"tablet\" data-v-9b0b6231>Tablet</option><option value=\"desktop\" data-v-9b0b6231>Desktop</option>", 5)])], 512), [[vModelSelect, $setup.typeFilter]])
		]), createBaseVNode("div", _hoisted_12$14, [createBaseVNode("div", _hoisted_13$14, [createBaseVNode("table", _hoisted_14$14, [_cache[32] || (_cache[32] = createBaseVNode("thead", { class: "bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700" }, [createBaseVNode("tr", null, [
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Device"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "User"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Type"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Status"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Online"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Connections"),
			createBaseVNode("th", { class: "px-3 py-2 text-right text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Actions")
		])], -1)), createBaseVNode("tbody", _hoisted_15$14, [(openBlock(true), createElementBlock(Fragment, null, renderList($setup.filteredDevices, (device) => {
			return openBlock(), createElementBlock("tr", {
				key: device.id,
				onClick: ($event) => $setup.openEditModal(device),
				class: "hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer"
			}, [
				createBaseVNode("td", _hoisted_17$14, [createBaseVNode("div", _hoisted_18$14, [_cache[27] || (_cache[27] = createBaseVNode("div", { class: "w-7 h-7 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center" }, [createBaseVNode("svg", {
					class: "w-4 h-4 text-white",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M17 1.01L7 1c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-1.99-2-1.99zM17 19H7V5h10v14z" })])], -1)), createBaseVNode("div", null, [createBaseVNode("p", _hoisted_19$13, toDisplayString(device.device_name || "Unknown"), 1), createBaseVNode("p", _hoisted_20$13, toDisplayString(device.mac_address), 1)])])]),
				createBaseVNode("td", _hoisted_21$13, toDisplayString(device.user_account || "N/A"), 1),
				createBaseVNode("td", _hoisted_22$13, [createBaseVNode("span", _hoisted_23$13, toDisplayString(device.device_type || "unknown"), 1)]),
				createBaseVNode("td", _hoisted_24$13, [createBaseVNode("span", { class: normalizeClass(["px-1.5 py-0.5 text-[10px] font-medium rounded-full", $setup.getStatusBadge(device.status)]) }, toDisplayString(device.status), 3)]),
				createBaseVNode("td", _hoisted_25$13, [createBaseVNode("span", { class: normalizeClass(["flex items-center gap-1 text-xs", device.is_online ? "text-emerald-600 dark:text-emerald-400" : "text-slate-400 dark:text-slate-600"]) }, [createBaseVNode("span", { class: normalizeClass(["w-1.5 h-1.5 rounded-full", device.is_online ? "bg-emerald-500" : "bg-slate-400"]) }, null, 2), createTextVNode(" " + toDisplayString(device.is_online ? "Online" : "Offline"), 1)], 2)]),
				createBaseVNode("td", _hoisted_26$13, toDisplayString(device.total_connections || 0), 1),
				createBaseVNode("td", _hoisted_27$12, [createBaseVNode("div", _hoisted_28$12, [
					createBaseVNode("button", {
						onClick: withModifiers(($event) => $setup.openEditModal(device), ["stop"]),
						class: "p-1 hover:bg-blue-100 dark:hover:bg-blue-600 rounded transition-colors",
						title: "Edit"
					}, [..._cache[28] || (_cache[28] = [createBaseVNode("svg", {
						class: "w-3.5 h-3.5 text-blue-600 dark:text-blue-400",
						fill: "none",
						stroke: "currentColor",
						viewBox: "0 0 24 24"
					}, [createBaseVNode("path", {
						"stroke-linecap": "round",
						"stroke-linejoin": "round",
						"stroke-width": "2",
						d: "M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
					})], -1)])], 8, _hoisted_29$12),
					device.status === "active" ? (openBlock(), createElementBlock("button", {
						key: 0,
						onClick: withModifiers(($event) => $setup.blockDevice(device), ["stop"]),
						class: "p-1 hover:bg-amber-100 dark:hover:bg-amber-600 rounded transition-colors",
						title: "Block"
					}, [..._cache[29] || (_cache[29] = [createBaseVNode("svg", {
						class: "w-3.5 h-3.5 text-amber-600 dark:text-amber-400",
						fill: "none",
						stroke: "currentColor",
						viewBox: "0 0 24 24"
					}, [createBaseVNode("path", {
						"stroke-linecap": "round",
						"stroke-linejoin": "round",
						"stroke-width": "2",
						d: "M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"
					})], -1)])], 8, _hoisted_30$12)) : (openBlock(), createElementBlock("button", {
						key: 1,
						onClick: withModifiers(($event) => $setup.unblockDevice(device), ["stop"]),
						class: "p-1 hover:bg-emerald-100 dark:hover:bg-emerald-600 rounded transition-colors",
						title: "Unblock"
					}, [..._cache[30] || (_cache[30] = [createBaseVNode("svg", {
						class: "w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400",
						fill: "none",
						stroke: "currentColor",
						viewBox: "0 0 24 24"
					}, [createBaseVNode("path", {
						"stroke-linecap": "round",
						"stroke-linejoin": "round",
						"stroke-width": "2",
						d: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
					})], -1)])], 8, _hoisted_31$12)),
					createBaseVNode("button", {
						onClick: withModifiers(($event) => $setup.openDeleteModal(device), ["stop"]),
						class: "p-1 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors",
						title: "Delete"
					}, [..._cache[31] || (_cache[31] = [createBaseVNode("svg", {
						class: "w-3.5 h-3.5 text-red-600 dark:text-red-400",
						fill: "none",
						stroke: "currentColor",
						viewBox: "0 0 24 24"
					}, [createBaseVNode("path", {
						"stroke-linecap": "round",
						"stroke-linejoin": "round",
						"stroke-width": "2",
						d: "M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
					})], -1)])], 8, _hoisted_32$12)
				])])
			], 8, _hoisted_16$14);
		}), 128))])])])])]),
		$setup.showFormModal ? (openBlock(), createElementBlock("div", {
			key: 1,
			class: "fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4",
			onClick: _cache[15] || (_cache[15] = withModifiers((...args) => $setup.closeFormModal && $setup.closeFormModal(...args), ["self"]))
		}, [createBaseVNode("div", _hoisted_33$12, [
			createBaseVNode("div", _hoisted_34$12, [createBaseVNode("h2", _hoisted_35$12, toDisplayString($setup.selectedDevice?.id ? "Edit Device" : "Add Device"), 1), createBaseVNode("button", {
				onClick: _cache[6] || (_cache[6] = (...args) => $setup.closeFormModal && $setup.closeFormModal(...args)),
				class: "p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
			}, [..._cache[33] || (_cache[33] = [createBaseVNode("svg", {
				class: "w-4 h-4",
				fill: "none",
				stroke: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M6 18L18 6M6 6l12 12"
			})], -1)])])]),
			createBaseVNode("div", _hoisted_36$12, [createBaseVNode("div", _hoisted_37$12, [
				createBaseVNode("div", null, [_cache[34] || (_cache[34] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "MAC Address", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => $setup.formData.mac_address = $event),
					type: "text",
					placeholder: "00:11:22:33:44:55",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.mac_address]])]),
				createBaseVNode("div", null, [_cache[35] || (_cache[35] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Device Name", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[8] || (_cache[8] = ($event) => $setup.formData.device_name = $event),
					type: "text",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.device_name]])]),
				createBaseVNode("div", null, [_cache[37] || (_cache[37] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Device Type", -1)), withDirectives(createBaseVNode("select", {
					"onUpdate:modelValue": _cache[9] || (_cache[9] = ($event) => $setup.formData.device_type = $event),
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, [..._cache[36] || (_cache[36] = [
					createBaseVNode("option", { value: "phone" }, "Phone", -1),
					createBaseVNode("option", { value: "laptop" }, "Laptop", -1),
					createBaseVNode("option", { value: "tablet" }, "Tablet", -1),
					createBaseVNode("option", { value: "desktop" }, "Desktop", -1)
				])], 512), [[vModelSelect, $setup.formData.device_type]])]),
				createBaseVNode("div", null, [_cache[39] || (_cache[39] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Platform", -1)), withDirectives(createBaseVNode("select", {
					"onUpdate:modelValue": _cache[10] || (_cache[10] = ($event) => $setup.formData.device_platform = $event),
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, [..._cache[38] || (_cache[38] = [createStaticVNode("<option value=\"windows\" data-v-9b0b6231>Windows</option><option value=\"macos\" data-v-9b0b6231>macOS</option><option value=\"linux\" data-v-9b0b6231>Linux</option><option value=\"android\" data-v-9b0b6231>Android</option><option value=\"ios\" data-v-9b0b6231>iOS</option>", 5)])], 512), [[vModelSelect, $setup.formData.device_platform]])]),
				createBaseVNode("div", null, [_cache[41] || (_cache[41] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Status", -1)), withDirectives(createBaseVNode("select", {
					"onUpdate:modelValue": _cache[11] || (_cache[11] = ($event) => $setup.formData.status = $event),
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, [..._cache[40] || (_cache[40] = [
					createBaseVNode("option", { value: "active" }, "Active", -1),
					createBaseVNode("option", { value: "inactive" }, "Inactive", -1),
					createBaseVNode("option", { value: "suspended" }, "Suspended", -1)
				])], 512), [[vModelSelect, $setup.formData.status]])]),
				createBaseVNode("div", _hoisted_38$12, [createBaseVNode("label", _hoisted_39$12, [withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[12] || (_cache[12] = ($event) => $setup.formData.is_trusted = $event),
					type: "checkbox",
					class: "w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded"
				}, null, 512), [[vModelCheckbox, $setup.formData.is_trusted]]), _cache[42] || (_cache[42] = createBaseVNode("span", { class: "text-xs text-slate-700 dark:text-slate-300" }, "Trusted Device", -1))])])
			])]),
			createBaseVNode("div", _hoisted_40$12, [createBaseVNode("button", {
				onClick: _cache[13] || (_cache[13] = (...args) => $setup.closeFormModal && $setup.closeFormModal(...args)),
				class: "px-3 py-2 text-xs bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg"
			}, "Cancel"), createBaseVNode("button", {
				onClick: _cache[14] || (_cache[14] = (...args) => $setup.saveDevice && $setup.saveDevice(...args)),
				disabled: $setup.saveLoading,
				class: normalizeClass(["px-3 py-2 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-lg", { "opacity-50": $setup.saveLoading }])
			}, toDisplayString($setup.saveLoading ? "Saving..." : $setup.selectedDevice?.id ? "Update" : "Create"), 11, _hoisted_41$11)])
		])])) : createCommentVNode("", true),
		createVNode(_component_ConfirmDialog, {
			show: $setup.showDeleteModal,
			title: "Delete Device",
			message: `Delete device ${$setup.deviceToDelete?.device_name}?`,
			type: "danger",
			onConfirm: $setup.confirmDelete,
			onCancel: $setup.closeDeleteModal
		}, null, 8, [
			"show",
			"message",
			"onConfirm",
			"onCancel"
		])
	]);
}
var Devices_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$18, [["render", _sfc_render$18], ["__scopeId", "data-v-9b0b6231"]]);
var _sfc_main$17 = {
	name: "Sessions",
	components: {
		ModernMetricCard: MetricCard_default,
		ConfirmDialog: ConfirmDialog_default
	},
	setup() {
		const { loading, error, makeRequest } = useApi();
		const sessions = ref([]);
		const stats = ref({});
		const searchTerm = ref("");
		const statusFilter = ref("");
		const showFormModal = ref(false);
		const showDeleteModal = ref(false);
		const selectedSession = ref(null);
		const sessionToDelete = ref(null);
		const saveLoading = ref(false);
		const deleteLoading = ref(false);
		const formData = ref({
			session_id: "",
			ip_address: "",
			is_active: true
		});
		const filteredSessions = computed(() => {
			let result = sessions.value;
			if (searchTerm.value) {
				const term = searchTerm.value.toLowerCase();
				result = result.filter((s) => s.session_id?.toLowerCase().includes(term) || s.user_account?.toLowerCase().includes(term) || s.ip_address?.includes(term));
			}
			if (statusFilter.value) result = result.filter((s) => s.is_active === (statusFilter.value === "true"));
			return result;
		});
		const fetchSessions = async () => {
			try {
				const data = await makeRequest("get", "suapi/sessions/");
				sessions.value = data.results || data;
			} catch (err) {
				console.error("Error:", err);
			}
		};
		const fetchStats = async () => {
			try {
				stats.value = await makeRequest("get", "suapi/sessions/stats/");
			} catch (err) {
				console.error("Error:", err);
			}
		};
		const refreshData = () => Promise.all([fetchSessions(), fetchStats()]);
		const openAddModal = () => {
			selectedSession.value = null;
			formData.value = {
				session_id: "",
				ip_address: "",
				is_active: true
			};
			showFormModal.value = true;
		};
		const openEditModal = (session) => {
			selectedSession.value = session;
			formData.value = {
				session_id: session.session_id || "",
				ip_address: session.ip_address || "",
				is_active: session.is_active || false
			};
			showFormModal.value = true;
		};
		const closeFormModal = () => {
			showFormModal.value = false;
			selectedSession.value = null;
			formData.value = {
				session_id: "",
				ip_address: "",
				is_active: true
			};
		};
		const saveSession = async () => {
			saveLoading.value = true;
			try {
				if (selectedSession.value?.id) await makeRequest("patch", `suapi/sessions/${selectedSession.value.id}/`, formData.value);
				else await makeRequest("post", "suapi/sessions/", formData.value);
				await refreshData();
				closeFormModal();
			} catch (err) {
				alert("Error: " + (err.response?.data?.error || err.message));
			} finally {
				saveLoading.value = false;
			}
		};
		const terminateSession = async (session) => {
			if (!confirm(`Terminate session ${session.session_id?.substring(0, 8)}?`)) return;
			try {
				await makeRequest("post", `suapi/sessions/${session.id}/terminate/`, { reason: "Admin action" });
				await refreshData();
			} catch (err) {
				alert("Error: " + (err.response?.data?.error || err.message));
			}
		};
		const openDeleteModal = (session) => {
			sessionToDelete.value = session;
			showDeleteModal.value = true;
		};
		const closeDeleteModal = () => {
			showDeleteModal.value = false;
			sessionToDelete.value = null;
		};
		const confirmDelete = async () => {
			deleteLoading.value = true;
			try {
				await makeRequest("delete", `suapi/sessions/${sessionToDelete.value.id}/`);
				await refreshData();
				closeDeleteModal();
			} catch (err) {
				alert("Error: " + (err.response?.data?.error || err.message));
			} finally {
				deleteLoading.value = false;
			}
		};
		onMounted(refreshData);
		return {
			loading,
			error,
			sessions,
			stats,
			searchTerm,
			statusFilter,
			showFormModal,
			showDeleteModal,
			selectedSession,
			sessionToDelete,
			saveLoading,
			deleteLoading,
			formData,
			filteredSessions,
			fetchSessions,
			refreshData,
			openAddModal,
			openEditModal,
			closeFormModal,
			saveSession,
			terminateSession,
			openDeleteModal,
			closeDeleteModal,
			confirmDelete
		};
	}
};
var _hoisted_1$17 = { class: "space-y-4 animate-fade-in" };
var _hoisted_2$17 = { class: "flex items-center justify-between" };
var _hoisted_3$17 = { class: "flex items-center gap-2" };
var _hoisted_4$17 = {
	key: 0,
	class: "bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-lg p-4"
};
var _hoisted_5$17 = { class: "flex items-center justify-between" };
var _hoisted_6$17 = { class: "flex items-center gap-3" };
var _hoisted_7$17 = { class: "text-xs text-rose-600 dark:text-rose-500 mt-1" };
var _hoisted_8$17 = { class: "grid grid-cols-2 md:grid-cols-4 gap-3 animate-slide-up" };
var _hoisted_9$15 = {
	class: "space-y-3 animate-slide-up",
	style: { "animation-delay": "0.1s" }
};
var _hoisted_10$14 = { class: "flex items-center gap-2" };
var _hoisted_11$13 = { class: "flex-1" };
var _hoisted_12$13 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden" };
var _hoisted_13$13 = { class: "overflow-x-auto" };
var _hoisted_14$13 = { class: "w-full" };
var _hoisted_15$13 = { class: "divide-y divide-slate-200 dark:divide-slate-700" };
var _hoisted_16$13 = ["onClick"];
var _hoisted_17$13 = { class: "px-3 py-2" };
var _hoisted_18$13 = { class: "flex items-center gap-2" };
var _hoisted_19$12 = { class: "text-xs font-medium text-slate-900 dark:text-white font-mono" };
var _hoisted_20$12 = { class: "text-[10px] text-slate-500 dark:text-slate-400" };
var _hoisted_21$12 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white" };
var _hoisted_22$12 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white" };
var _hoisted_23$12 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white font-mono" };
var _hoisted_24$12 = { class: "px-3 py-2" };
var _hoisted_25$12 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white" };
var _hoisted_26$12 = { class: "px-3 py-2 text-right" };
var _hoisted_27$11 = { class: "flex items-center justify-end gap-0.5" };
var _hoisted_28$11 = ["onClick"];
var _hoisted_29$11 = ["onClick"];
var _hoisted_30$11 = ["onClick"];
var _hoisted_31$11 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden" };
var _hoisted_32$11 = { class: "flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700" };
var _hoisted_33$11 = { class: "text-base font-semibold text-slate-900 dark:text-white" };
var _hoisted_34$11 = { class: "p-5 overflow-y-auto max-h-[calc(90vh-140px)]" };
var _hoisted_35$11 = { class: "grid grid-cols-2 gap-4" };
var _hoisted_36$11 = { class: "col-span-2" };
var _hoisted_37$11 = { class: "flex items-center" };
var _hoisted_38$11 = { class: "flex items-center gap-2 cursor-pointer" };
var _hoisted_39$11 = { class: "flex items-center justify-end gap-2 p-5 border-t border-slate-200 dark:border-slate-700" };
var _hoisted_40$11 = ["disabled"];
function _sfc_render$17(_ctx, _cache, $props, $setup, $data, $options) {
	const _component_ModernMetricCard = resolveComponent("ModernMetricCard");
	const _component_ConfirmDialog = resolveComponent("ConfirmDialog");
	return openBlock(), createElementBlock("div", _hoisted_1$17, [
		createBaseVNode("div", _hoisted_2$17, [_cache[14] || (_cache[14] = createBaseVNode("div", null, [createBaseVNode("h1", { class: "text-lg font-semibold text-slate-900 dark:text-white" }, "Sessions"), createBaseVNode("p", { class: "text-xs text-slate-500 dark:text-slate-400 mt-0.5" }, "Monitor active user sessions")], -1)), createBaseVNode("div", _hoisted_3$17, [createBaseVNode("button", {
			onClick: _cache[0] || (_cache[0] = (...args) => $setup.openAddModal && $setup.openAddModal(...args)),
			class: "px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-xs flex items-center gap-1.5"
		}, [..._cache[12] || (_cache[12] = [createBaseVNode("svg", {
			class: "w-3.5 h-3.5",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M12 4v16m8-8H4"
		})], -1), createTextVNode(" Add Session ", -1)])]), createBaseVNode("button", {
			onClick: _cache[1] || (_cache[1] = (...args) => $setup.refreshData && $setup.refreshData(...args)),
			class: normalizeClass(["p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors", { "animate-spin": $setup.loading }])
		}, [..._cache[13] || (_cache[13] = [createBaseVNode("svg", {
			class: "w-4 h-4 text-slate-600 dark:text-slate-400",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
		})], -1)])], 2)])]),
		$setup.error ? (openBlock(), createElementBlock("div", _hoisted_4$17, [createBaseVNode("div", _hoisted_5$17, [createBaseVNode("div", _hoisted_6$17, [_cache[16] || (_cache[16] = createBaseVNode("svg", {
			class: "w-5 h-5 text-rose-600 dark:text-rose-400",
			fill: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" })], -1)), createBaseVNode("div", null, [_cache[15] || (_cache[15] = createBaseVNode("h3", { class: "text-sm font-medium text-rose-800 dark:text-rose-400" }, "Failed to load sessions", -1)), createBaseVNode("p", _hoisted_7$17, toDisplayString($setup.error), 1)])]), createBaseVNode("button", {
			onClick: _cache[2] || (_cache[2] = (...args) => $setup.fetchSessions && $setup.fetchSessions(...args)),
			class: "px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm"
		}, "Retry")])])) : createCommentVNode("", true),
		createBaseVNode("div", _hoisted_8$17, [
			createVNode(_component_ModernMetricCard, {
				title: "Total",
				value: $setup.stats.total_sessions,
				color: "blue"
			}, {
				default: withCtx(() => [..._cache[17] || (_cache[17] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Active",
				value: $setup.stats.active_sessions,
				color: "emerald"
			}, {
				default: withCtx(() => [..._cache[18] || (_cache[18] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Vouchers",
				value: $setup.stats.voucher_sessions,
				color: "purple"
			}, {
				default: withCtx(() => [..._cache[19] || (_cache[19] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7C4.67 7 4 6.33 4 5.5S4.67 4 5.5 4 7 4.67 7 5.5 6.33 7 5.5 7z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Inactive",
				value: $setup.stats.inactive_sessions,
				color: "slate"
			}, {
				default: withCtx(() => [..._cache[20] || (_cache[20] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm5 11H7v-2h10v2z" })], -1)])]),
				_: 1
			}, 8, ["value"])
		]),
		createBaseVNode("div", _hoisted_9$15, [createBaseVNode("div", _hoisted_10$14, [createBaseVNode("div", _hoisted_11$13, [withDirectives(createBaseVNode("input", {
			"onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => $setup.searchTerm = $event),
			type: "text",
			placeholder: "Search sessions...",
			class: "w-full px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs"
		}, null, 512), [[vModelText, $setup.searchTerm]])]), withDirectives(createBaseVNode("select", {
			"onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => $setup.statusFilter = $event),
			class: "px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs"
		}, [..._cache[21] || (_cache[21] = [
			createBaseVNode("option", { value: "" }, "All Status", -1),
			createBaseVNode("option", { value: "true" }, "Active", -1),
			createBaseVNode("option", { value: "false" }, "Inactive", -1)
		])], 512), [[vModelSelect, $setup.statusFilter]])]), createBaseVNode("div", _hoisted_12$13, [createBaseVNode("div", _hoisted_13$13, [createBaseVNode("table", _hoisted_14$13, [_cache[26] || (_cache[26] = createBaseVNode("thead", { class: "bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700" }, [createBaseVNode("tr", null, [
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Session"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "User"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Device"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "IP Address"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Status"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Duration"),
			createBaseVNode("th", { class: "px-3 py-2 text-right text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Actions")
		])], -1)), createBaseVNode("tbody", _hoisted_15$13, [(openBlock(true), createElementBlock(Fragment, null, renderList($setup.filteredSessions, (session) => {
			return openBlock(), createElementBlock("tr", {
				key: session.id,
				onClick: ($event) => $setup.openEditModal(session),
				class: "hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer"
			}, [
				createBaseVNode("td", _hoisted_17$13, [createBaseVNode("div", _hoisted_18$13, [_cache[22] || (_cache[22] = createBaseVNode("div", { class: "w-7 h-7 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center" }, [createBaseVNode("svg", {
					class: "w-4 h-4 text-white",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z" })])], -1)), createBaseVNode("div", null, [createBaseVNode("p", _hoisted_19$12, toDisplayString(session.session_id?.substring(0, 8)), 1), createBaseVNode("p", _hoisted_20$12, "ID: " + toDisplayString(session.id), 1)])])]),
				createBaseVNode("td", _hoisted_21$12, toDisplayString(session.user_account || "N/A"), 1),
				createBaseVNode("td", _hoisted_22$12, toDisplayString(session.device_name || "Unknown"), 1),
				createBaseVNode("td", _hoisted_23$12, toDisplayString(session.ip_address || "N/A"), 1),
				createBaseVNode("td", _hoisted_24$12, [createBaseVNode("span", { class: normalizeClass(["px-1.5 py-0.5 text-[10px] font-medium rounded-full", session.is_active ? "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400" : "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400"]) }, toDisplayString(session.is_active ? "Active" : "Inactive"), 3)]),
				createBaseVNode("td", _hoisted_25$12, toDisplayString(session.duration || "N/A"), 1),
				createBaseVNode("td", _hoisted_26$12, [createBaseVNode("div", _hoisted_27$11, [
					createBaseVNode("button", {
						onClick: withModifiers(($event) => $setup.openEditModal(session), ["stop"]),
						class: "p-1 hover:bg-blue-100 dark:hover:bg-blue-600 rounded transition-colors",
						title: "Edit"
					}, [..._cache[23] || (_cache[23] = [createBaseVNode("svg", {
						class: "w-3.5 h-3.5 text-blue-600 dark:text-blue-400",
						fill: "none",
						stroke: "currentColor",
						viewBox: "0 0 24 24"
					}, [createBaseVNode("path", {
						"stroke-linecap": "round",
						"stroke-linejoin": "round",
						"stroke-width": "2",
						d: "M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
					})], -1)])], 8, _hoisted_28$11),
					session.is_active ? (openBlock(), createElementBlock("button", {
						key: 0,
						onClick: withModifiers(($event) => $setup.terminateSession(session), ["stop"]),
						class: "p-1 hover:bg-amber-100 dark:hover:bg-amber-600 rounded transition-colors",
						title: "Terminate"
					}, [..._cache[24] || (_cache[24] = [createBaseVNode("svg", {
						class: "w-3.5 h-3.5 text-amber-600 dark:text-amber-400",
						fill: "none",
						stroke: "currentColor",
						viewBox: "0 0 24 24"
					}, [createBaseVNode("path", {
						"stroke-linecap": "round",
						"stroke-linejoin": "round",
						"stroke-width": "2",
						d: "M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
					}), createBaseVNode("path", {
						"stroke-linecap": "round",
						"stroke-linejoin": "round",
						"stroke-width": "2",
						d: "M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"
					})], -1)])], 8, _hoisted_29$11)) : createCommentVNode("", true),
					createBaseVNode("button", {
						onClick: withModifiers(($event) => $setup.openDeleteModal(session), ["stop"]),
						class: "p-1 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors",
						title: "Delete"
					}, [..._cache[25] || (_cache[25] = [createBaseVNode("svg", {
						class: "w-3.5 h-3.5 text-red-600 dark:text-red-400",
						fill: "none",
						stroke: "currentColor",
						viewBox: "0 0 24 24"
					}, [createBaseVNode("path", {
						"stroke-linecap": "round",
						"stroke-linejoin": "round",
						"stroke-width": "2",
						d: "M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
					})], -1)])], 8, _hoisted_30$11)
				])])
			], 8, _hoisted_16$13);
		}), 128))])])])])]),
		$setup.showFormModal ? (openBlock(), createElementBlock("div", {
			key: 1,
			class: "fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4",
			onClick: _cache[11] || (_cache[11] = withModifiers((...args) => $setup.closeFormModal && $setup.closeFormModal(...args), ["self"]))
		}, [createBaseVNode("div", _hoisted_31$11, [
			createBaseVNode("div", _hoisted_32$11, [createBaseVNode("h2", _hoisted_33$11, toDisplayString($setup.selectedSession?.id ? "Edit Session" : "Add Session"), 1), createBaseVNode("button", {
				onClick: _cache[5] || (_cache[5] = (...args) => $setup.closeFormModal && $setup.closeFormModal(...args)),
				class: "p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
			}, [..._cache[27] || (_cache[27] = [createBaseVNode("svg", {
				class: "w-4 h-4",
				fill: "none",
				stroke: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M6 18L18 6M6 6l12 12"
			})], -1)])])]),
			createBaseVNode("div", _hoisted_34$11, [createBaseVNode("div", _hoisted_35$11, [
				createBaseVNode("div", _hoisted_36$11, [_cache[28] || (_cache[28] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Session ID", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => $setup.formData.session_id = $event),
					type: "text",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white",
					disabled: ""
				}, null, 512), [[vModelText, $setup.formData.session_id]])]),
				createBaseVNode("div", null, [_cache[29] || (_cache[29] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "IP Address", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => $setup.formData.ip_address = $event),
					type: "text",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.ip_address]])]),
				createBaseVNode("div", _hoisted_37$11, [createBaseVNode("label", _hoisted_38$11, [withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[8] || (_cache[8] = ($event) => $setup.formData.is_active = $event),
					type: "checkbox",
					class: "w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded"
				}, null, 512), [[vModelCheckbox, $setup.formData.is_active]]), _cache[30] || (_cache[30] = createBaseVNode("span", { class: "text-xs text-slate-700 dark:text-slate-300" }, "Active Session", -1))])])
			])]),
			createBaseVNode("div", _hoisted_39$11, [createBaseVNode("button", {
				onClick: _cache[9] || (_cache[9] = (...args) => $setup.closeFormModal && $setup.closeFormModal(...args)),
				class: "px-3 py-2 text-xs bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg"
			}, "Cancel"), createBaseVNode("button", {
				onClick: _cache[10] || (_cache[10] = (...args) => $setup.saveSession && $setup.saveSession(...args)),
				disabled: $setup.saveLoading,
				class: normalizeClass(["px-3 py-2 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-lg", { "opacity-50": $setup.saveLoading }])
			}, toDisplayString($setup.saveLoading ? "Saving..." : $setup.selectedSession?.id ? "Update" : "Create"), 11, _hoisted_40$11)])
		])])) : createCommentVNode("", true),
		createVNode(_component_ConfirmDialog, {
			show: $setup.showDeleteModal,
			title: "Delete Session",
			message: `Delete session ${$setup.sessionToDelete?.session_id?.substring(0, 8)}?`,
			type: "danger",
			onConfirm: $setup.confirmDelete,
			onCancel: $setup.closeDeleteModal
		}, null, 8, [
			"show",
			"message",
			"onConfirm",
			"onCancel"
		])
	]);
}
var Sessions_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$17, [["render", _sfc_render$17], ["__scopeId", "data-v-dfcfdc4b"]]);
var _sfc_main$16 = {
	name: "Packages",
	components: {
		ModernMetricCard: MetricCard_default,
		ConfirmDialog: ConfirmDialog_default
	},
	setup() {
		const { loading, error, makeRequest } = useApi();
		const packages = ref([]);
		const stats = ref({});
		const searchTerm = ref("");
		const statusFilter = ref("");
		const showFormModal = ref(false);
		const showDeleteModal = ref(false);
		const selectedPackage = ref(null);
		const packageToDelete = ref(null);
		const saveLoading = ref(false);
		const deleteLoading = ref(false);
		const formData = ref({
			name: "",
			code: "",
			category: "time_based_unlimited",
			tier: "basic",
			price: 0,
			duration_hours: 1,
			speed_limit_mbps: 10,
			data_limit_mb: null,
			device_limit: 1,
			qos_priority: "standard",
			description: "",
			is_active: true,
			is_public: true
		});
		const filteredPackages = computed(() => {
			let result = packages.value;
			if (searchTerm.value) {
				const term = searchTerm.value.toLowerCase();
				result = result.filter((p) => p.name?.toLowerCase().includes(term));
			}
			if (statusFilter.value) result = result.filter((p) => p.is_active === (statusFilter.value === "true"));
			return result;
		});
		const fetchPackages = async () => {
			try {
				const data = await makeRequest("get", "suapi/packages/");
				packages.value = data.results || data;
			} catch (err) {
				console.error("Error:", err);
			}
		};
		const fetchStats = async () => {
			try {
				stats.value = await makeRequest("get", "suapi/packages/stats/");
			} catch (err) {
				console.error("Error:", err);
			}
		};
		const refreshData = () => Promise.all([fetchPackages(), fetchStats()]);
		const formatNumber = (num) => new Intl.NumberFormat().format(num);
		const formatDuration = (duration) => {
			if (!duration) return "N/A";
			const match = duration.match(/PT(\d+)H/);
			return match ? `${match[1]}h` : duration;
		};
		const formatData = (mb) => {
			if (!mb) return "Unlimited";
			if (mb >= 1024) return `${(mb / 1024).toFixed(1)} GB`;
			return `${mb} MB`;
		};
		const openAddModal = () => {
			selectedPackage.value = null;
			formData.value = {
				name: "",
				code: "",
				category: "time_based_unlimited",
				tier: "basic",
				price: 0,
				duration_hours: 1,
				speed_limit_mbps: 10,
				data_limit_mb: null,
				device_limit: 1,
				qos_priority: "standard",
				description: "",
				is_active: true,
				is_public: true
			};
			showFormModal.value = true;
		};
		const openEditModal = (pkg) => {
			selectedPackage.value = pkg;
			formData.value = {
				name: pkg.name || "",
				code: pkg.code || "",
				category: pkg.category || "time_based_unlimited",
				tier: pkg.tier || "basic",
				price: pkg.price || 0,
				duration_hours: pkg.duration_hours || 1,
				speed_limit_mbps: pkg.speed_limit_mbps || 10,
				data_limit_mb: pkg.data_limit_mb || null,
				device_limit: pkg.device_limit || 1,
				qos_priority: pkg.qos_priority || "standard",
				description: pkg.description || "",
				is_active: pkg.is_active || false,
				is_public: pkg.is_public || false
			};
			showFormModal.value = true;
		};
		const closeFormModal = () => {
			showFormModal.value = false;
			selectedPackage.value = null;
			formData.value = {
				name: "",
				price: 0,
				data_limit_gb: 0,
				validity_days: 0,
				description: "",
				is_active: true
			};
		};
		const savePackage = async () => {
			saveLoading.value = true;
			try {
				const payload = { ...formData.value };
				payload.duration = `PT${payload.duration_hours}H`;
				delete payload.duration_hours;
				if (selectedPackage.value?.id) await makeRequest("patch", `suapi/packages/${selectedPackage.value.id}/`, payload);
				else await makeRequest("post", "suapi/packages/", payload);
				await refreshData();
				closeFormModal();
			} catch (err) {
				alert("Error: " + (err.response?.data?.error || JSON.stringify(err.response?.data) || err.message));
			} finally {
				saveLoading.value = false;
			}
		};
		const openDeleteModal = (pkg) => {
			packageToDelete.value = pkg;
			showDeleteModal.value = true;
		};
		const closeDeleteModal = () => {
			showDeleteModal.value = false;
			packageToDelete.value = null;
		};
		const confirmDelete = async () => {
			deleteLoading.value = true;
			try {
				await makeRequest("delete", `suapi/packages/${packageToDelete.value.id}/`);
				await refreshData();
				closeDeleteModal();
			} catch (err) {
				alert("Error: " + (err.response?.data?.error || err.message));
			} finally {
				deleteLoading.value = false;
			}
		};
		onMounted(refreshData);
		return {
			loading,
			error,
			packages,
			stats,
			searchTerm,
			statusFilter,
			showFormModal,
			showDeleteModal,
			selectedPackage,
			packageToDelete,
			saveLoading,
			deleteLoading,
			formData,
			filteredPackages,
			fetchPackages,
			refreshData,
			formatNumber,
			formatDuration,
			formatData,
			openAddModal,
			openEditModal,
			closeFormModal,
			savePackage,
			openDeleteModal,
			closeDeleteModal,
			confirmDelete
		};
	}
};
var _hoisted_1$16 = { class: "space-y-4 animate-fade-in" };
var _hoisted_2$16 = { class: "flex items-center justify-between" };
var _hoisted_3$16 = { class: "flex items-center gap-2" };
var _hoisted_4$16 = {
	key: 0,
	class: "bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-lg p-4"
};
var _hoisted_5$16 = { class: "flex items-center justify-between" };
var _hoisted_6$16 = { class: "flex items-center gap-3" };
var _hoisted_7$16 = { class: "text-xs text-rose-600 dark:text-rose-500 mt-1" };
var _hoisted_8$16 = { class: "grid grid-cols-2 md:grid-cols-4 gap-3 animate-slide-up" };
var _hoisted_9$14 = {
	class: "space-y-3 animate-slide-up",
	style: { "animation-delay": "0.1s" }
};
var _hoisted_10$13 = { class: "flex items-center gap-2" };
var _hoisted_11$12 = { class: "flex-1" };
var _hoisted_12$12 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden" };
var _hoisted_13$12 = { class: "overflow-x-auto" };
var _hoisted_14$12 = { class: "w-full" };
var _hoisted_15$12 = { class: "divide-y divide-slate-200 dark:divide-slate-700" };
var _hoisted_16$12 = ["onClick"];
var _hoisted_17$12 = { class: "px-3 py-2" };
var _hoisted_18$12 = { class: "flex items-center gap-2" };
var _hoisted_19$11 = { class: "text-xs font-medium text-slate-900 dark:text-white" };
var _hoisted_20$11 = { class: "text-[10px] text-slate-500 dark:text-slate-400" };
var _hoisted_21$11 = { class: "px-3 py-2 text-xs font-mono text-slate-900 dark:text-white" };
var _hoisted_22$11 = { class: "px-3 py-2" };
var _hoisted_23$11 = { class: "px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400" };
var _hoisted_24$11 = { class: "px-3 py-2" };
var _hoisted_25$11 = { class: "px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400" };
var _hoisted_26$11 = { class: "px-3 py-2 text-xs font-semibold text-slate-900 dark:text-white" };
var _hoisted_27$10 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white" };
var _hoisted_28$10 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white" };
var _hoisted_29$10 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white" };
var _hoisted_30$10 = { class: "px-3 py-2" };
var _hoisted_31$10 = { class: "px-3 py-2 text-right" };
var _hoisted_32$10 = { class: "flex items-center justify-end gap-0.5" };
var _hoisted_33$10 = ["onClick"];
var _hoisted_34$10 = ["onClick"];
var _hoisted_35$10 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden" };
var _hoisted_36$10 = { class: "flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700" };
var _hoisted_37$10 = { class: "text-base font-semibold text-slate-900 dark:text-white" };
var _hoisted_38$10 = { class: "p-5 overflow-y-auto max-h-[calc(90vh-140px)]" };
var _hoisted_39$10 = { class: "grid grid-cols-2 gap-4" };
var _hoisted_40$10 = { class: "col-span-2" };
var _hoisted_41$10 = { class: "flex items-center" };
var _hoisted_42$9 = { class: "flex items-center gap-2 cursor-pointer" };
var _hoisted_43$8 = { class: "flex items-center" };
var _hoisted_44$8 = { class: "flex items-center gap-2 cursor-pointer" };
var _hoisted_45$5 = { class: "col-span-2" };
var _hoisted_46$5 = { class: "flex items-center justify-end gap-2 p-5 border-t border-slate-200 dark:border-slate-700" };
var _hoisted_47$5 = ["disabled"];
function _sfc_render$16(_ctx, _cache, $props, $setup, $data, $options) {
	const _component_ModernMetricCard = resolveComponent("ModernMetricCard");
	const _component_ConfirmDialog = resolveComponent("ConfirmDialog");
	return openBlock(), createElementBlock("div", _hoisted_1$16, [
		createBaseVNode("div", _hoisted_2$16, [_cache[24] || (_cache[24] = createBaseVNode("div", null, [createBaseVNode("h1", { class: "text-lg font-semibold text-slate-900 dark:text-white" }, "Packages"), createBaseVNode("p", { class: "text-xs text-slate-500 dark:text-slate-400 mt-0.5" }, "Manage data packages")], -1)), createBaseVNode("div", _hoisted_3$16, [createBaseVNode("button", {
			onClick: _cache[0] || (_cache[0] = (...args) => $setup.openAddModal && $setup.openAddModal(...args)),
			class: "px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-xs flex items-center gap-1.5"
		}, [..._cache[22] || (_cache[22] = [createBaseVNode("svg", {
			class: "w-3.5 h-3.5",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M12 4v16m8-8H4"
		})], -1), createTextVNode(" Add Package ", -1)])]), createBaseVNode("button", {
			onClick: _cache[1] || (_cache[1] = (...args) => $setup.refreshData && $setup.refreshData(...args)),
			class: normalizeClass(["p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors", { "animate-spin": $setup.loading }])
		}, [..._cache[23] || (_cache[23] = [createBaseVNode("svg", {
			class: "w-4 h-4 text-slate-600 dark:text-slate-400",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
		})], -1)])], 2)])]),
		$setup.error ? (openBlock(), createElementBlock("div", _hoisted_4$16, [createBaseVNode("div", _hoisted_5$16, [createBaseVNode("div", _hoisted_6$16, [_cache[26] || (_cache[26] = createBaseVNode("svg", {
			class: "w-5 h-5 text-rose-600 dark:text-rose-400",
			fill: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" })], -1)), createBaseVNode("div", null, [_cache[25] || (_cache[25] = createBaseVNode("h3", { class: "text-sm font-medium text-rose-800 dark:text-rose-400" }, "Failed to load packages", -1)), createBaseVNode("p", _hoisted_7$16, toDisplayString($setup.error), 1)])]), createBaseVNode("button", {
			onClick: _cache[2] || (_cache[2] = (...args) => $setup.fetchPackages && $setup.fetchPackages(...args)),
			class: "px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm"
		}, "Retry")])])) : createCommentVNode("", true),
		createBaseVNode("div", _hoisted_8$16, [
			createVNode(_component_ModernMetricCard, {
				title: "Total",
				value: $setup.stats.total_packages,
				color: "blue"
			}, {
				default: withCtx(() => [..._cache[27] || (_cache[27] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4zM6 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm13.5-9l1.96 2.5H17V9.5h2.5zm-1.5 9c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Active",
				value: $setup.stats.active_packages,
				color: "emerald"
			}, {
				default: withCtx(() => [..._cache[28] || (_cache[28] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Popular",
				value: $setup.stats.popular_packages,
				color: "purple"
			}, {
				default: withCtx(() => [..._cache[29] || (_cache[29] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Avg Price",
				value: `KSh ${$setup.formatNumber($setup.stats.average_price || 0)}`,
				color: "amber"
			}, {
				default: withCtx(() => [..._cache[30] || (_cache[30] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z" })], -1)])]),
				_: 1
			}, 8, ["value"])
		]),
		createBaseVNode("div", _hoisted_9$14, [createBaseVNode("div", _hoisted_10$13, [createBaseVNode("div", _hoisted_11$12, [withDirectives(createBaseVNode("input", {
			"onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => $setup.searchTerm = $event),
			type: "text",
			placeholder: "Search packages...",
			class: "w-full px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs"
		}, null, 512), [[vModelText, $setup.searchTerm]])]), withDirectives(createBaseVNode("select", {
			"onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => $setup.statusFilter = $event),
			class: "px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs"
		}, [..._cache[31] || (_cache[31] = [
			createBaseVNode("option", { value: "" }, "All Status", -1),
			createBaseVNode("option", { value: "true" }, "Active", -1),
			createBaseVNode("option", { value: "false" }, "Inactive", -1)
		])], 512), [[vModelSelect, $setup.statusFilter]])]), createBaseVNode("div", _hoisted_12$12, [createBaseVNode("div", _hoisted_13$12, [createBaseVNode("table", _hoisted_14$12, [_cache[35] || (_cache[35] = createBaseVNode("thead", { class: "bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700" }, [createBaseVNode("tr", null, [
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Package"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Code"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Category"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Tier"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Price"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Duration"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Speed"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Data"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Status"),
			createBaseVNode("th", { class: "px-3 py-2 text-right text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Actions")
		])], -1)), createBaseVNode("tbody", _hoisted_15$12, [(openBlock(true), createElementBlock(Fragment, null, renderList($setup.filteredPackages, (pkg) => {
			return openBlock(), createElementBlock("tr", {
				key: pkg.id,
				onClick: ($event) => $setup.openEditModal(pkg),
				class: "hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer"
			}, [
				createBaseVNode("td", _hoisted_17$12, [createBaseVNode("div", _hoisted_18$12, [_cache[32] || (_cache[32] = createBaseVNode("div", { class: "w-7 h-7 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center" }, [createBaseVNode("svg", {
					class: "w-4 h-4 text-white",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4z" })])], -1)), createBaseVNode("div", null, [createBaseVNode("p", _hoisted_19$11, toDisplayString(pkg.name), 1), createBaseVNode("p", _hoisted_20$11, "ID: " + toDisplayString(pkg.id), 1)])])]),
				createBaseVNode("td", _hoisted_21$11, toDisplayString(pkg.code), 1),
				createBaseVNode("td", _hoisted_22$11, [createBaseVNode("span", _hoisted_23$11, toDisplayString(pkg.category), 1)]),
				createBaseVNode("td", _hoisted_24$11, [createBaseVNode("span", _hoisted_25$11, toDisplayString(pkg.tier), 1)]),
				createBaseVNode("td", _hoisted_26$11, "KSh " + toDisplayString($setup.formatNumber(pkg.price)), 1),
				createBaseVNode("td", _hoisted_27$10, toDisplayString($setup.formatDuration(pkg.duration)), 1),
				createBaseVNode("td", _hoisted_28$10, toDisplayString(pkg.speed_limit_mbps) + " Mbps", 1),
				createBaseVNode("td", _hoisted_29$10, toDisplayString($setup.formatData(pkg.data_limit_mb)), 1),
				createBaseVNode("td", _hoisted_30$10, [createBaseVNode("span", { class: normalizeClass(["px-1.5 py-0.5 text-[10px] font-medium rounded-full", pkg.is_active ? "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400" : "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400"]) }, toDisplayString(pkg.is_active ? "Active" : "Inactive"), 3)]),
				createBaseVNode("td", _hoisted_31$10, [createBaseVNode("div", _hoisted_32$10, [createBaseVNode("button", {
					onClick: withModifiers(($event) => $setup.openEditModal(pkg), ["stop"]),
					class: "p-1 hover:bg-blue-100 dark:hover:bg-blue-600 rounded transition-colors",
					title: "Edit"
				}, [..._cache[33] || (_cache[33] = [createBaseVNode("svg", {
					class: "w-3.5 h-3.5 text-blue-600 dark:text-blue-400",
					fill: "none",
					stroke: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", {
					"stroke-linecap": "round",
					"stroke-linejoin": "round",
					"stroke-width": "2",
					d: "M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
				})], -1)])], 8, _hoisted_33$10), createBaseVNode("button", {
					onClick: withModifiers(($event) => $setup.openDeleteModal(pkg), ["stop"]),
					class: "p-1 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors",
					title: "Delete"
				}, [..._cache[34] || (_cache[34] = [createBaseVNode("svg", {
					class: "w-3.5 h-3.5 text-red-600 dark:text-red-400",
					fill: "none",
					stroke: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", {
					"stroke-linecap": "round",
					"stroke-linejoin": "round",
					"stroke-width": "2",
					d: "M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
				})], -1)])], 8, _hoisted_34$10)])])
			], 8, _hoisted_16$12);
		}), 128))])])])])]),
		$setup.showFormModal ? (openBlock(), createElementBlock("div", {
			key: 1,
			class: "fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4",
			onClick: _cache[21] || (_cache[21] = withModifiers((...args) => $setup.closeFormModal && $setup.closeFormModal(...args), ["self"]))
		}, [createBaseVNode("div", _hoisted_35$10, [
			createBaseVNode("div", _hoisted_36$10, [createBaseVNode("h2", _hoisted_37$10, toDisplayString($setup.selectedPackage?.id ? "Edit Package" : "Add Package"), 1), createBaseVNode("button", {
				onClick: _cache[5] || (_cache[5] = (...args) => $setup.closeFormModal && $setup.closeFormModal(...args)),
				class: "p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
			}, [..._cache[36] || (_cache[36] = [createBaseVNode("svg", {
				class: "w-4 h-4",
				fill: "none",
				stroke: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M6 18L18 6M6 6l12 12"
			})], -1)])])]),
			createBaseVNode("div", _hoisted_38$10, [createBaseVNode("div", _hoisted_39$10, [
				createBaseVNode("div", _hoisted_40$10, [_cache[37] || (_cache[37] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Package Name *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => $setup.formData.name = $event),
					type: "text",
					required: "",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.name]])]),
				createBaseVNode("div", null, [_cache[38] || (_cache[38] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Code *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => $setup.formData.code = $event),
					type: "text",
					required: "",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.code]])]),
				createBaseVNode("div", null, [_cache[40] || (_cache[40] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Category *", -1)), withDirectives(createBaseVNode("select", {
					"onUpdate:modelValue": _cache[8] || (_cache[8] = ($event) => $setup.formData.category = $event),
					required: "",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, [..._cache[39] || (_cache[39] = [createStaticVNode("<option value=\"time_based_unlimited\" data-v-547842f1>Time-Based-Unlimited</option><option value=\"data_based\" data-v-547842f1>Data-Based</option><option value=\"unlimited\" data-v-547842f1>Unlimited</option><option value=\"hybrid\" data-v-547842f1>Hybrid</option><option value=\"corporate\" data-v-547842f1>Corporate</option>", 5)])], 512), [[vModelSelect, $setup.formData.category]])]),
				createBaseVNode("div", null, [_cache[42] || (_cache[42] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Tier *", -1)), withDirectives(createBaseVNode("select", {
					"onUpdate:modelValue": _cache[9] || (_cache[9] = ($event) => $setup.formData.tier = $event),
					required: "",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, [..._cache[41] || (_cache[41] = [createStaticVNode("<option value=\"basic\" data-v-547842f1>Basic</option><option value=\"standard\" data-v-547842f1>Standard</option><option value=\"premium\" data-v-547842f1>Premium</option><option value=\"business\" data-v-547842f1>Business</option><option value=\"enterprise\" data-v-547842f1>Enterprise</option>", 5)])], 512), [[vModelSelect, $setup.formData.tier]])]),
				createBaseVNode("div", null, [_cache[43] || (_cache[43] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Price (KSh) *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[10] || (_cache[10] = ($event) => $setup.formData.price = $event),
					type: "number",
					step: "0.01",
					required: "",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.price]])]),
				createBaseVNode("div", null, [_cache[44] || (_cache[44] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Duration (hours) *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[11] || (_cache[11] = ($event) => $setup.formData.duration_hours = $event),
					type: "number",
					required: "",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.duration_hours]])]),
				createBaseVNode("div", null, [_cache[45] || (_cache[45] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Speed Limit (Mbps) *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[12] || (_cache[12] = ($event) => $setup.formData.speed_limit_mbps = $event),
					type: "number",
					required: "",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.speed_limit_mbps]])]),
				createBaseVNode("div", null, [_cache[46] || (_cache[46] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Data Limit (MB)", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[13] || (_cache[13] = ($event) => $setup.formData.data_limit_mb = $event),
					type: "number",
					placeholder: "Leave blank for unlimited",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.data_limit_mb]])]),
				createBaseVNode("div", null, [_cache[47] || (_cache[47] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Device Limit", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[14] || (_cache[14] = ($event) => $setup.formData.device_limit = $event),
					type: "number",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.device_limit]])]),
				createBaseVNode("div", null, [_cache[49] || (_cache[49] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "QoS Priority", -1)), withDirectives(createBaseVNode("select", {
					"onUpdate:modelValue": _cache[15] || (_cache[15] = ($event) => $setup.formData.qos_priority = $event),
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, [..._cache[48] || (_cache[48] = [
					createBaseVNode("option", { value: "standard" }, "Standard", -1),
					createBaseVNode("option", { value: "premium" }, "Premium", -1),
					createBaseVNode("option", { value: "business" }, "Business", -1),
					createBaseVNode("option", { value: "real_time" }, "Real-time", -1)
				])], 512), [[vModelSelect, $setup.formData.qos_priority]])]),
				createBaseVNode("div", _hoisted_41$10, [createBaseVNode("label", _hoisted_42$9, [withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[16] || (_cache[16] = ($event) => $setup.formData.is_active = $event),
					type: "checkbox",
					class: "w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded"
				}, null, 512), [[vModelCheckbox, $setup.formData.is_active]]), _cache[50] || (_cache[50] = createBaseVNode("span", { class: "text-xs text-slate-700 dark:text-slate-300" }, "Active Package", -1))])]),
				createBaseVNode("div", _hoisted_43$8, [createBaseVNode("label", _hoisted_44$8, [withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[17] || (_cache[17] = ($event) => $setup.formData.is_public = $event),
					type: "checkbox",
					class: "w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded"
				}, null, 512), [[vModelCheckbox, $setup.formData.is_public]]), _cache[51] || (_cache[51] = createBaseVNode("span", { class: "text-xs text-slate-700 dark:text-slate-300" }, "Public Package", -1))])]),
				createBaseVNode("div", _hoisted_45$5, [_cache[52] || (_cache[52] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Description", -1)), withDirectives(createBaseVNode("textarea", {
					"onUpdate:modelValue": _cache[18] || (_cache[18] = ($event) => $setup.formData.description = $event),
					rows: "3",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.description]])])
			])]),
			createBaseVNode("div", _hoisted_46$5, [createBaseVNode("button", {
				onClick: _cache[19] || (_cache[19] = (...args) => $setup.closeFormModal && $setup.closeFormModal(...args)),
				class: "px-3 py-2 text-xs bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg"
			}, "Cancel"), createBaseVNode("button", {
				onClick: _cache[20] || (_cache[20] = (...args) => $setup.savePackage && $setup.savePackage(...args)),
				disabled: $setup.saveLoading,
				class: normalizeClass(["px-3 py-2 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-lg", { "opacity-50": $setup.saveLoading }])
			}, toDisplayString($setup.saveLoading ? "Saving..." : $setup.selectedPackage?.id ? "Update" : "Create"), 11, _hoisted_47$5)])
		])])) : createCommentVNode("", true),
		createVNode(_component_ConfirmDialog, {
			show: $setup.showDeleteModal,
			title: "Delete Package",
			message: `Delete package ${$setup.packageToDelete?.name}?`,
			type: "danger",
			onConfirm: $setup.confirmDelete,
			onCancel: $setup.closeDeleteModal
		}, null, 8, [
			"show",
			"message",
			"onConfirm",
			"onCancel"
		])
	]);
}
var Packages_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$16, [["render", _sfc_render$16], ["__scopeId", "data-v-547842f1"]]);
var _sfc_main$15 = {
	name: "Vouchers",
	components: {
		ModernMetricCard: MetricCard_default,
		ConfirmDialog: ConfirmDialog_default
	},
	setup() {
		const { loading, error, makeRequest } = useApi();
		const vouchers = ref([]);
		const stats = ref({});
		const searchTerm = ref("");
		const statusFilter = ref("");
		const showFormModal = ref(false);
		const showDeleteModal = ref(false);
		const selectedVoucher = ref(null);
		const voucherToDelete = ref(null);
		const saveLoading = ref(false);
		const deleteLoading = ref(false);
		const formData = ref({
			user: "",
			package: "",
			price_paid: 0,
			expires_at: ""
		});
		const filteredVouchers = computed(() => {
			let result = vouchers.value;
			if (searchTerm.value) {
				const term = searchTerm.value.toLowerCase();
				result = result.filter((v) => v.user_username?.toLowerCase().includes(term) || v.package_name?.toLowerCase().includes(term) || v.voucher_code?.toLowerCase().includes(term));
			}
			if (statusFilter.value) result = result.filter((v) => v.status === statusFilter.value);
			return result;
		});
		const fetchVouchers = async () => {
			try {
				const data = await makeRequest("get", "suapi/vouchers/");
				vouchers.value = data.results || data;
			} catch (err) {
				console.error("Error:", err);
			}
		};
		const fetchStats = async () => {
			try {
				stats.value = await makeRequest("get", "suapi/vouchers/stats/");
			} catch (err) {
				console.error("Error:", err);
			}
		};
		const refreshData = () => Promise.all([fetchVouchers(), fetchStats()]);
		const formatNumber = (num) => new Intl.NumberFormat().format(num || 0);
		const formatDate = (date) => date ? new Date(date).toLocaleDateString() : "N/A";
		const formatBytes = (bytes) => {
			if (!bytes) return "0 B";
			const k = 1024;
			const sizes = [
				"B",
				"KB",
				"MB",
				"GB"
			];
			const i = Math.floor(Math.log(bytes) / Math.log(k));
			return Math.round(bytes / Math.pow(k, i) * 100) / 100 + " " + sizes[i];
		};
		const openAddModal = () => {
			selectedVoucher.value = null;
			formData.value = {
				user: "",
				package: "",
				price_paid: 0,
				expires_at: ""
			};
			showFormModal.value = true;
		};
		const openEditModal = (voucher) => {
			selectedVoucher.value = voucher;
			formData.value = {
				user: voucher.user || "",
				package: voucher.package || "",
				price_paid: voucher.price_paid || 0,
				expires_at: voucher.expires_at || ""
			};
			showFormModal.value = true;
		};
		const closeFormModal = () => {
			showFormModal.value = false;
			selectedVoucher.value = null;
			formData.value = {
				user: "",
				package: "",
				price_paid: 0,
				expires_at: ""
			};
		};
		const saveVoucher = async () => {
			saveLoading.value = true;
			try {
				if (selectedVoucher.value?.id) await makeRequest("patch", `suapi/vouchers/${selectedVoucher.value.id}/`, formData.value);
				else await makeRequest("post", "suapi/vouchers/", formData.value);
				await refreshData();
				closeFormModal();
			} catch (err) {
				alert("Error: " + (err.response?.data?.error || err.message));
			} finally {
				saveLoading.value = false;
			}
		};
		const openDeleteModal = (voucher) => {
			voucherToDelete.value = voucher;
			showDeleteModal.value = true;
		};
		const closeDeleteModal = () => {
			showDeleteModal.value = false;
			voucherToDelete.value = null;
		};
		const confirmDelete = async () => {
			deleteLoading.value = true;
			try {
				await makeRequest("delete", `suapi/vouchers/${voucherToDelete.value.id}/`);
				await refreshData();
				closeDeleteModal();
			} catch (err) {
				alert("Error: " + (err.response?.data?.error || err.message));
			} finally {
				deleteLoading.value = false;
			}
		};
		const getStatusBadge = (status) => {
			const badges = {
				"active": "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400",
				"expired": "bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400",
				"exhausted": "bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400",
				"suspended": "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400",
				"cancelled": "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400"
			};
			return badges[status] || badges.suspended;
		};
		onMounted(refreshData);
		return {
			loading,
			error,
			vouchers,
			stats,
			searchTerm,
			statusFilter,
			showFormModal,
			showDeleteModal,
			selectedVoucher,
			voucherToDelete,
			saveLoading,
			deleteLoading,
			formData,
			filteredVouchers,
			fetchVouchers,
			refreshData,
			formatNumber,
			formatDate,
			formatBytes,
			openAddModal,
			openEditModal,
			closeFormModal,
			saveVoucher,
			openDeleteModal,
			closeDeleteModal,
			confirmDelete,
			getStatusBadge
		};
	}
};
var _hoisted_1$15 = { class: "space-y-4 animate-fade-in" };
var _hoisted_2$15 = { class: "flex items-center justify-between" };
var _hoisted_3$15 = { class: "flex items-center gap-2" };
var _hoisted_4$15 = {
	key: 0,
	class: "bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-lg p-4"
};
var _hoisted_5$15 = { class: "flex items-center justify-between" };
var _hoisted_6$15 = { class: "flex items-center gap-3" };
var _hoisted_7$15 = { class: "text-xs text-rose-600 dark:text-rose-500 mt-1" };
var _hoisted_8$15 = { class: "grid grid-cols-2 md:grid-cols-4 gap-3 animate-slide-up" };
var _hoisted_9$13 = {
	class: "space-y-3 animate-slide-up",
	style: { "animation-delay": "0.1s" }
};
var _hoisted_10$12 = { class: "flex items-center gap-2" };
var _hoisted_11$11 = { class: "flex-1" };
var _hoisted_12$11 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden" };
var _hoisted_13$11 = { class: "overflow-x-auto" };
var _hoisted_14$11 = { class: "w-full" };
var _hoisted_15$11 = { class: "divide-y divide-slate-200 dark:divide-slate-700" };
var _hoisted_16$11 = ["onClick"];
var _hoisted_17$11 = { class: "px-3 py-2" };
var _hoisted_18$11 = { class: "flex items-center gap-2" };
var _hoisted_19$10 = { class: "text-xs font-medium text-slate-900 dark:text-white font-mono" };
var _hoisted_20$10 = { class: "text-[10px] text-slate-500 dark:text-slate-400" };
var _hoisted_21$10 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white" };
var _hoisted_22$10 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white" };
var _hoisted_23$10 = { class: "px-3 py-2 text-xs font-semibold text-slate-900 dark:text-white" };
var _hoisted_24$10 = { class: "px-3 py-2" };
var _hoisted_25$10 = { class: "text-xs text-slate-900 dark:text-white" };
var _hoisted_26$10 = { class: "flex items-center gap-1" };
var _hoisted_27$9 = { class: "text-[10px]" };
var _hoisted_28$9 = { class: "flex items-center gap-1" };
var _hoisted_29$9 = { class: "text-[10px]" };
var _hoisted_30$9 = { class: "text-[10px] font-semibold text-slate-600 dark:text-slate-400 mt-0.5" };
var _hoisted_31$9 = { class: "px-3 py-2" };
var _hoisted_32$9 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white" };
var _hoisted_33$9 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white" };
var _hoisted_34$9 = { class: "px-3 py-2 text-right" };
var _hoisted_35$9 = { class: "flex items-center justify-end gap-0.5" };
var _hoisted_36$9 = ["onClick"];
var _hoisted_37$9 = ["onClick"];
var _hoisted_38$9 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden" };
var _hoisted_39$9 = { class: "flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700" };
var _hoisted_40$9 = { class: "text-base font-semibold text-slate-900 dark:text-white" };
var _hoisted_41$9 = { class: "p-5 overflow-y-auto max-h-[calc(90vh-140px)]" };
var _hoisted_42$8 = { class: "grid grid-cols-2 gap-4" };
var _hoisted_43$7 = { class: "flex items-center justify-end gap-2 p-5 border-t border-slate-200 dark:border-slate-700" };
var _hoisted_44$7 = ["disabled"];
function _sfc_render$15(_ctx, _cache, $props, $setup, $data, $options) {
	const _component_ModernMetricCard = resolveComponent("ModernMetricCard");
	const _component_ConfirmDialog = resolveComponent("ConfirmDialog");
	return openBlock(), createElementBlock("div", _hoisted_1$15, [
		createBaseVNode("div", _hoisted_2$15, [_cache[15] || (_cache[15] = createBaseVNode("div", null, [createBaseVNode("h1", { class: "text-lg font-semibold text-slate-900 dark:text-white" }, "Vouchers"), createBaseVNode("p", { class: "text-xs text-slate-500 dark:text-slate-400 mt-0.5" }, "Manage dispatch vouchers")], -1)), createBaseVNode("div", _hoisted_3$15, [createBaseVNode("button", {
			onClick: _cache[0] || (_cache[0] = (...args) => $setup.openAddModal && $setup.openAddModal(...args)),
			class: "px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-xs flex items-center gap-1.5"
		}, [..._cache[13] || (_cache[13] = [createBaseVNode("svg", {
			class: "w-3.5 h-3.5",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M12 4v16m8-8H4"
		})], -1), createTextVNode(" Add Voucher ", -1)])]), createBaseVNode("button", {
			onClick: _cache[1] || (_cache[1] = (...args) => $setup.refreshData && $setup.refreshData(...args)),
			class: normalizeClass(["p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors", { "animate-spin": $setup.loading }])
		}, [..._cache[14] || (_cache[14] = [createBaseVNode("svg", {
			class: "w-4 h-4 text-slate-600 dark:text-slate-400",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
		})], -1)])], 2)])]),
		$setup.error ? (openBlock(), createElementBlock("div", _hoisted_4$15, [createBaseVNode("div", _hoisted_5$15, [createBaseVNode("div", _hoisted_6$15, [_cache[17] || (_cache[17] = createBaseVNode("svg", {
			class: "w-5 h-5 text-rose-600 dark:text-rose-400",
			fill: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" })], -1)), createBaseVNode("div", null, [_cache[16] || (_cache[16] = createBaseVNode("h3", { class: "text-sm font-medium text-rose-800 dark:text-rose-400" }, "Failed to load vouchers", -1)), createBaseVNode("p", _hoisted_7$15, toDisplayString($setup.error), 1)])]), createBaseVNode("button", {
			onClick: _cache[2] || (_cache[2] = (...args) => $setup.fetchVouchers && $setup.fetchVouchers(...args)),
			class: "px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm"
		}, "Retry")])])) : createCommentVNode("", true),
		createBaseVNode("div", _hoisted_8$15, [
			createVNode(_component_ModernMetricCard, {
				title: "Total",
				value: $setup.stats.total_vouchers,
				color: "blue"
			}, {
				default: withCtx(() => [..._cache[18] || (_cache[18] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7C4.67 7 4 6.33 4 5.5S4.67 4 5.5 4 7 4.67 7 5.5 6.33 7 5.5 7z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Active",
				value: $setup.stats.active_vouchers,
				color: "emerald"
			}, {
				default: withCtx(() => [..._cache[19] || (_cache[19] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Expired",
				value: $setup.stats.expired_vouchers,
				color: "amber"
			}, {
				default: withCtx(() => [..._cache[20] || (_cache[20] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Revenue",
				value: `KSh ${$setup.formatNumber($setup.stats.total_revenue || 0)}`,
				color: "purple"
			}, {
				default: withCtx(() => [..._cache[21] || (_cache[21] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z" })], -1)])]),
				_: 1
			}, 8, ["value"])
		]),
		createBaseVNode("div", _hoisted_9$13, [createBaseVNode("div", _hoisted_10$12, [createBaseVNode("div", _hoisted_11$11, [withDirectives(createBaseVNode("input", {
			"onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => $setup.searchTerm = $event),
			type: "text",
			placeholder: "Search vouchers...",
			class: "w-full px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs"
		}, null, 512), [[vModelText, $setup.searchTerm]])]), withDirectives(createBaseVNode("select", {
			"onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => $setup.statusFilter = $event),
			class: "px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs"
		}, [..._cache[22] || (_cache[22] = [
			createBaseVNode("option", { value: "" }, "All Status", -1),
			createBaseVNode("option", { value: "active" }, "Active", -1),
			createBaseVNode("option", { value: "expired" }, "Expired", -1),
			createBaseVNode("option", { value: "used" }, "Used", -1)
		])], 512), [[vModelSelect, $setup.statusFilter]])]), createBaseVNode("div", _hoisted_12$11, [createBaseVNode("div", _hoisted_13$11, [createBaseVNode("table", _hoisted_14$11, [_cache[28] || (_cache[28] = createBaseVNode("thead", { class: "bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700" }, [createBaseVNode("tr", null, [
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Voucher"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "User"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Package"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Price"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Usage"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Status"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Activated"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Expires"),
			createBaseVNode("th", { class: "px-3 py-2 text-right text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Actions")
		])], -1)), createBaseVNode("tbody", _hoisted_15$11, [(openBlock(true), createElementBlock(Fragment, null, renderList($setup.filteredVouchers, (voucher) => {
			return openBlock(), createElementBlock("tr", {
				key: voucher.id,
				onClick: ($event) => $setup.openEditModal(voucher),
				class: "hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer"
			}, [
				createBaseVNode("td", _hoisted_17$11, [createBaseVNode("div", _hoisted_18$11, [_cache[23] || (_cache[23] = createBaseVNode("div", { class: "w-7 h-7 rounded-lg bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center" }, [createBaseVNode("svg", {
					class: "w-4 h-4 text-white",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42z" })])], -1)), createBaseVNode("div", null, [createBaseVNode("p", _hoisted_19$10, toDisplayString(voucher.voucher_code), 1), createBaseVNode("p", _hoisted_20$10, "Sessions: " + toDisplayString(voucher.session_count || 0), 1)])])]),
				createBaseVNode("td", _hoisted_21$10, toDisplayString(voucher.user_username || "N/A"), 1),
				createBaseVNode("td", _hoisted_22$10, toDisplayString(voucher.package_name || "N/A"), 1),
				createBaseVNode("td", _hoisted_23$10, "KSh " + toDisplayString($setup.formatNumber(voucher.price_paid)), 1),
				createBaseVNode("td", _hoisted_24$10, [createBaseVNode("div", _hoisted_25$10, [
					createBaseVNode("div", _hoisted_26$10, [_cache[24] || (_cache[24] = createBaseVNode("svg", {
						class: "w-3 h-3 text-blue-500",
						fill: "currentColor",
						viewBox: "0 0 24 24"
					}, [createBaseVNode("path", { d: "M7 10l5 5 5-5z" })], -1)), createBaseVNode("span", _hoisted_27$9, toDisplayString($setup.formatBytes(voucher.download_bytes)), 1)]),
					createBaseVNode("div", _hoisted_28$9, [_cache[25] || (_cache[25] = createBaseVNode("svg", {
						class: "w-3 h-3 text-green-500",
						fill: "currentColor",
						viewBox: "0 0 24 24"
					}, [createBaseVNode("path", { d: "M7 14l5-5 5 5z" })], -1)), createBaseVNode("span", _hoisted_29$9, toDisplayString($setup.formatBytes(voucher.upload_bytes)), 1)]),
					createBaseVNode("div", _hoisted_30$9, " Total: " + toDisplayString($setup.formatBytes((voucher.download_bytes || 0) + (voucher.upload_bytes || 0))), 1)
				])]),
				createBaseVNode("td", _hoisted_31$9, [createBaseVNode("span", { class: normalizeClass(["px-1.5 py-0.5 text-[10px] font-medium rounded-full", $setup.getStatusBadge(voucher.status)]) }, toDisplayString(voucher.status), 3)]),
				createBaseVNode("td", _hoisted_32$9, toDisplayString($setup.formatDate(voucher.activated_at)), 1),
				createBaseVNode("td", _hoisted_33$9, toDisplayString($setup.formatDate(voucher.expires_at)), 1),
				createBaseVNode("td", _hoisted_34$9, [createBaseVNode("div", _hoisted_35$9, [createBaseVNode("button", {
					onClick: withModifiers(($event) => $setup.openEditModal(voucher), ["stop"]),
					class: "p-1 hover:bg-blue-100 dark:hover:bg-blue-600 rounded transition-colors",
					title: "Edit"
				}, [..._cache[26] || (_cache[26] = [createBaseVNode("svg", {
					class: "w-3.5 h-3.5 text-blue-600 dark:text-blue-400",
					fill: "none",
					stroke: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", {
					"stroke-linecap": "round",
					"stroke-linejoin": "round",
					"stroke-width": "2",
					d: "M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
				})], -1)])], 8, _hoisted_36$9), createBaseVNode("button", {
					onClick: withModifiers(($event) => $setup.openDeleteModal(voucher), ["stop"]),
					class: "p-1 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors",
					title: "Delete"
				}, [..._cache[27] || (_cache[27] = [createBaseVNode("svg", {
					class: "w-3.5 h-3.5 text-red-600 dark:text-red-400",
					fill: "none",
					stroke: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", {
					"stroke-linecap": "round",
					"stroke-linejoin": "round",
					"stroke-width": "2",
					d: "M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
				})], -1)])], 8, _hoisted_37$9)])])
			], 8, _hoisted_16$11);
		}), 128))])])])])]),
		$setup.showFormModal ? (openBlock(), createElementBlock("div", {
			key: 1,
			class: "fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4",
			onClick: _cache[12] || (_cache[12] = withModifiers((...args) => $setup.closeFormModal && $setup.closeFormModal(...args), ["self"]))
		}, [createBaseVNode("div", _hoisted_38$9, [
			createBaseVNode("div", _hoisted_39$9, [createBaseVNode("h2", _hoisted_40$9, toDisplayString($setup.selectedVoucher?.id ? "Edit Voucher" : "Add Voucher"), 1), createBaseVNode("button", {
				onClick: _cache[5] || (_cache[5] = (...args) => $setup.closeFormModal && $setup.closeFormModal(...args)),
				class: "p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
			}, [..._cache[29] || (_cache[29] = [createBaseVNode("svg", {
				class: "w-4 h-4",
				fill: "none",
				stroke: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M6 18L18 6M6 6l12 12"
			})], -1)])])]),
			createBaseVNode("div", _hoisted_41$9, [createBaseVNode("div", _hoisted_42$8, [
				createBaseVNode("div", null, [_cache[30] || (_cache[30] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "User ID", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => $setup.formData.user = $event),
					type: "number",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.user]])]),
				createBaseVNode("div", null, [_cache[31] || (_cache[31] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Package ID", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => $setup.formData.package = $event),
					type: "number",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.package]])]),
				createBaseVNode("div", null, [_cache[32] || (_cache[32] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Price Paid (KSh)", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[8] || (_cache[8] = ($event) => $setup.formData.price_paid = $event),
					type: "number",
					step: "0.01",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.price_paid]])]),
				createBaseVNode("div", null, [_cache[33] || (_cache[33] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Expires At", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[9] || (_cache[9] = ($event) => $setup.formData.expires_at = $event),
					type: "datetime-local",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.expires_at]])])
			])]),
			createBaseVNode("div", _hoisted_43$7, [createBaseVNode("button", {
				onClick: _cache[10] || (_cache[10] = (...args) => $setup.closeFormModal && $setup.closeFormModal(...args)),
				class: "px-3 py-2 text-xs bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg"
			}, "Cancel"), createBaseVNode("button", {
				onClick: _cache[11] || (_cache[11] = (...args) => $setup.saveVoucher && $setup.saveVoucher(...args)),
				disabled: $setup.saveLoading,
				class: normalizeClass(["px-3 py-2 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-lg", { "opacity-50": $setup.saveLoading }])
			}, toDisplayString($setup.saveLoading ? "Saving..." : $setup.selectedVoucher?.id ? "Update" : "Create"), 11, _hoisted_44$7)])
		])])) : createCommentVNode("", true),
		createVNode(_component_ConfirmDialog, {
			show: $setup.showDeleteModal,
			title: "Delete Voucher",
			message: `Delete voucher ${$setup.voucherToDelete?.voucher_code}?`,
			type: "danger",
			onConfirm: $setup.confirmDelete,
			onCancel: $setup.closeDeleteModal
		}, null, 8, [
			"show",
			"message",
			"onConfirm",
			"onCancel"
		])
	]);
}
var Vouchers_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$15, [["render", _sfc_render$15], ["__scopeId", "data-v-2308f34b"]]);
var _sfc_main$14 = {
	name: "Coupons",
	components: {
		ModernMetricCard: MetricCard_default,
		ConfirmDialog: ConfirmDialog_default
	},
	setup() {
		const { loading, error, makeRequest } = useApi();
		const coupons = ref([]);
		const stats = ref({});
		const searchTerm = ref("");
		const statusFilter = ref("");
		const showFormModal = ref(false);
		const showDeleteModal = ref(false);
		const selectedCoupon = ref(null);
		const couponToDelete = ref(null);
		const saveLoading = ref(false);
		const formData = ref({
			code: "",
			name: "",
			coupon_type: "percentage",
			discount_value: 0,
			max_uses: 100,
			valid_until: "",
			is_active: true,
			is_reward: false,
			description: ""
		});
		const filteredCoupons = computed(() => {
			let result = coupons.value;
			if (searchTerm.value) {
				const term = searchTerm.value.toLowerCase();
				result = result.filter((c) => c.code?.toLowerCase().includes(term) || c.name?.toLowerCase().includes(term));
			}
			if (statusFilter.value) result = result.filter((c) => c.is_active === (statusFilter.value === "true"));
			return result;
		});
		const fetchCoupons = async () => {
			try {
				const data = await makeRequest("get", "suapi/coupons/");
				coupons.value = data.results || data;
			} catch (err) {
				console.error("Error:", err);
			}
		};
		const fetchStats = async () => {
			try {
				stats.value = await makeRequest("get", "suapi/coupons/stats/");
			} catch (err) {
				console.error("Error:", err);
			}
		};
		const refreshData = () => Promise.all([fetchCoupons(), fetchStats()]);
		const formatDate = (date) => date ? new Date(date).toLocaleDateString() : "N/A";
		const formatDiscount = (coupon) => coupon.coupon_type === "percentage" ? `${coupon.discount_value}%` : `KSh ${coupon.discount_value}`;
		const openAddModal = () => {
			selectedCoupon.value = null;
			formData.value = {
				code: "",
				name: "",
				coupon_type: "percentage",
				discount_value: 0,
				max_uses: 100,
				valid_until: "",
				is_active: true,
				is_reward: false,
				description: ""
			};
			showFormModal.value = true;
		};
		const openEditModal = (coupon) => {
			selectedCoupon.value = coupon;
			formData.value = {
				code: coupon.code || "",
				name: coupon.name || "",
				coupon_type: coupon.coupon_type || "percentage",
				discount_value: coupon.discount_value || 0,
				max_uses: coupon.max_uses || 100,
				valid_until: coupon.valid_until || "",
				is_active: coupon.is_active || false,
				is_reward: coupon.is_reward || false,
				description: coupon.description || ""
			};
			showFormModal.value = true;
		};
		const closeFormModal = () => {
			showFormModal.value = false;
			selectedCoupon.value = null;
			formData.value = {
				code: "",
				name: "",
				coupon_type: "percentage",
				discount_value: 0,
				max_uses: 100,
				valid_until: "",
				is_active: true,
				is_reward: false,
				description: ""
			};
		};
		const saveCoupon = async () => {
			saveLoading.value = true;
			try {
				if (selectedCoupon.value?.id) await makeRequest("patch", `suapi/coupons/${selectedCoupon.value.id}/`, formData.value);
				else await makeRequest("post", "suapi/coupons/", formData.value);
				await refreshData();
				closeFormModal();
			} catch (err) {
				alert("Error: " + (err.response?.data?.error || JSON.stringify(err.response?.data) || err.message));
			} finally {
				saveLoading.value = false;
			}
		};
		const openDeleteModal = (coupon) => {
			couponToDelete.value = coupon;
			showDeleteModal.value = true;
		};
		const closeDeleteModal = () => {
			showDeleteModal.value = false;
			couponToDelete.value = null;
		};
		const confirmDelete = async () => {
			try {
				await makeRequest("delete", `suapi/coupons/${couponToDelete.value.id}/`);
				await refreshData();
				closeDeleteModal();
			} catch (err) {
				alert("Error: " + (err.response?.data?.error || err.message));
			}
		};
		onMounted(refreshData);
		return {
			loading,
			error,
			coupons,
			stats,
			searchTerm,
			statusFilter,
			showFormModal,
			showDeleteModal,
			selectedCoupon,
			couponToDelete,
			saveLoading,
			formData,
			filteredCoupons,
			fetchCoupons,
			refreshData,
			formatDate,
			formatDiscount,
			openAddModal,
			openEditModal,
			closeFormModal,
			saveCoupon,
			openDeleteModal,
			closeDeleteModal,
			confirmDelete
		};
	}
};
var _hoisted_1$14 = { class: "space-y-4 animate-fade-in" };
var _hoisted_2$14 = { class: "flex items-center justify-between" };
var _hoisted_3$14 = { class: "flex items-center gap-2" };
var _hoisted_4$14 = {
	key: 0,
	class: "bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-lg p-4"
};
var _hoisted_5$14 = { class: "flex items-center justify-between" };
var _hoisted_6$14 = { class: "flex items-center gap-3" };
var _hoisted_7$14 = { class: "text-xs text-rose-600 dark:text-rose-500 mt-1" };
var _hoisted_8$14 = { class: "grid grid-cols-2 md:grid-cols-4 gap-3 animate-slide-up" };
var _hoisted_9$12 = {
	class: "space-y-3 animate-slide-up",
	style: { "animation-delay": "0.1s" }
};
var _hoisted_10$11 = { class: "flex items-center gap-2" };
var _hoisted_11$10 = { class: "flex-1" };
var _hoisted_12$10 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden" };
var _hoisted_13$10 = { class: "overflow-x-auto" };
var _hoisted_14$10 = { class: "w-full" };
var _hoisted_15$10 = { class: "divide-y divide-slate-200 dark:divide-slate-700" };
var _hoisted_16$10 = ["onClick"];
var _hoisted_17$10 = { class: "px-3 py-2" };
var _hoisted_18$10 = { class: "flex items-center gap-2" };
var _hoisted_19$9 = { class: "text-xs font-medium text-slate-900 dark:text-white font-mono" };
var _hoisted_20$9 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white" };
var _hoisted_21$9 = { class: "px-3 py-2" };
var _hoisted_22$9 = { class: "px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400" };
var _hoisted_23$9 = { class: "px-3 py-2 text-xs font-semibold text-slate-900 dark:text-white" };
var _hoisted_24$9 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white" };
var _hoisted_25$9 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white" };
var _hoisted_26$9 = { class: "px-3 py-2" };
var _hoisted_27$8 = { class: "px-3 py-2 text-right" };
var _hoisted_28$8 = { class: "flex items-center justify-end gap-0.5" };
var _hoisted_29$8 = ["onClick"];
var _hoisted_30$8 = ["onClick"];
var _hoisted_31$8 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden" };
var _hoisted_32$8 = { class: "flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700" };
var _hoisted_33$8 = { class: "text-base font-semibold text-slate-900 dark:text-white" };
var _hoisted_34$8 = { class: "p-5 overflow-y-auto max-h-[calc(90vh-140px)]" };
var _hoisted_35$8 = { class: "grid grid-cols-2 gap-4" };
var _hoisted_36$8 = { class: "flex items-center" };
var _hoisted_37$8 = { class: "flex items-center gap-2 cursor-pointer" };
var _hoisted_38$8 = { class: "flex items-center" };
var _hoisted_39$8 = { class: "flex items-center gap-2 cursor-pointer" };
var _hoisted_40$8 = { class: "col-span-2" };
var _hoisted_41$8 = { class: "flex items-center justify-end gap-2 p-5 border-t border-slate-200 dark:border-slate-700" };
var _hoisted_42$7 = ["disabled"];
function _sfc_render$14(_ctx, _cache, $props, $setup, $data, $options) {
	const _component_ModernMetricCard = resolveComponent("ModernMetricCard");
	const _component_ConfirmDialog = resolveComponent("ConfirmDialog");
	return openBlock(), createElementBlock("div", _hoisted_1$14, [
		createBaseVNode("div", _hoisted_2$14, [_cache[20] || (_cache[20] = createBaseVNode("div", null, [createBaseVNode("h1", { class: "text-lg font-semibold text-slate-900 dark:text-white" }, "Coupons"), createBaseVNode("p", { class: "text-xs text-slate-500 dark:text-slate-400 mt-0.5" }, "Manage discount coupons")], -1)), createBaseVNode("div", _hoisted_3$14, [createBaseVNode("button", {
			onClick: _cache[0] || (_cache[0] = (...args) => $setup.openAddModal && $setup.openAddModal(...args)),
			class: "px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-xs flex items-center gap-1.5"
		}, [..._cache[18] || (_cache[18] = [createBaseVNode("svg", {
			class: "w-3.5 h-3.5",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M12 4v16m8-8H4"
		})], -1), createTextVNode(" Add Coupon ", -1)])]), createBaseVNode("button", {
			onClick: _cache[1] || (_cache[1] = (...args) => $setup.refreshData && $setup.refreshData(...args)),
			class: normalizeClass(["p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors", { "animate-spin": $setup.loading }])
		}, [..._cache[19] || (_cache[19] = [createBaseVNode("svg", {
			class: "w-4 h-4 text-slate-600 dark:text-slate-400",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
		})], -1)])], 2)])]),
		$setup.error ? (openBlock(), createElementBlock("div", _hoisted_4$14, [createBaseVNode("div", _hoisted_5$14, [createBaseVNode("div", _hoisted_6$14, [_cache[22] || (_cache[22] = createBaseVNode("svg", {
			class: "w-5 h-5 text-rose-600 dark:text-rose-400",
			fill: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" })], -1)), createBaseVNode("div", null, [_cache[21] || (_cache[21] = createBaseVNode("h3", { class: "text-sm font-medium text-rose-800 dark:text-rose-400" }, "Failed to load coupons", -1)), createBaseVNode("p", _hoisted_7$14, toDisplayString($setup.error), 1)])]), createBaseVNode("button", {
			onClick: _cache[2] || (_cache[2] = (...args) => $setup.fetchCoupons && $setup.fetchCoupons(...args)),
			class: "px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm"
		}, "Retry")])])) : createCommentVNode("", true),
		createBaseVNode("div", _hoisted_8$14, [
			createVNode(_component_ModernMetricCard, {
				title: "Total",
				value: $setup.stats.total_coupons,
				color: "blue"
			}, {
				default: withCtx(() => [..._cache[23] || (_cache[23] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M20 4H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Active",
				value: $setup.stats.active_coupons,
				color: "emerald"
			}, {
				default: withCtx(() => [..._cache[24] || (_cache[24] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Reward",
				value: $setup.stats.reward_coupons,
				color: "purple"
			}, {
				default: withCtx(() => [..._cache[25] || (_cache[25] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Valid",
				value: $setup.stats.valid_coupons,
				color: "amber"
			}, {
				default: withCtx(() => [..._cache[26] || (_cache[26] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" })], -1)])]),
				_: 1
			}, 8, ["value"])
		]),
		createBaseVNode("div", _hoisted_9$12, [createBaseVNode("div", _hoisted_10$11, [createBaseVNode("div", _hoisted_11$10, [withDirectives(createBaseVNode("input", {
			"onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => $setup.searchTerm = $event),
			type: "text",
			placeholder: "Search coupons...",
			class: "w-full px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs"
		}, null, 512), [[vModelText, $setup.searchTerm]])]), withDirectives(createBaseVNode("select", {
			"onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => $setup.statusFilter = $event),
			class: "px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs"
		}, [..._cache[27] || (_cache[27] = [
			createBaseVNode("option", { value: "" }, "All Status", -1),
			createBaseVNode("option", { value: "true" }, "Active", -1),
			createBaseVNode("option", { value: "false" }, "Inactive", -1)
		])], 512), [[vModelSelect, $setup.statusFilter]])]), createBaseVNode("div", _hoisted_12$10, [createBaseVNode("div", _hoisted_13$10, [createBaseVNode("table", _hoisted_14$10, [_cache[31] || (_cache[31] = createBaseVNode("thead", { class: "bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700" }, [createBaseVNode("tr", null, [
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Code"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Name"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Type"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Discount"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Usage"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Valid Until"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Status"),
			createBaseVNode("th", { class: "px-3 py-2 text-right text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Actions")
		])], -1)), createBaseVNode("tbody", _hoisted_15$10, [(openBlock(true), createElementBlock(Fragment, null, renderList($setup.filteredCoupons, (coupon) => {
			return openBlock(), createElementBlock("tr", {
				key: coupon.id,
				onClick: ($event) => $setup.openEditModal(coupon),
				class: "hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer"
			}, [
				createBaseVNode("td", _hoisted_17$10, [createBaseVNode("div", _hoisted_18$10, [_cache[28] || (_cache[28] = createBaseVNode("div", { class: "w-7 h-7 rounded-lg bg-gradient-to-br from-pink-500 to-rose-600 flex items-center justify-center" }, [createBaseVNode("svg", {
					class: "w-4 h-4 text-white",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M20 4H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2z" })])], -1)), createBaseVNode("p", _hoisted_19$9, toDisplayString(coupon.code), 1)])]),
				createBaseVNode("td", _hoisted_20$9, toDisplayString(coupon.name), 1),
				createBaseVNode("td", _hoisted_21$9, [createBaseVNode("span", _hoisted_22$9, toDisplayString(coupon.coupon_type), 1)]),
				createBaseVNode("td", _hoisted_23$9, toDisplayString($setup.formatDiscount(coupon)), 1),
				createBaseVNode("td", _hoisted_24$9, toDisplayString(coupon.current_uses || 0) + " / " + toDisplayString(coupon.max_uses), 1),
				createBaseVNode("td", _hoisted_25$9, toDisplayString($setup.formatDate(coupon.valid_until)), 1),
				createBaseVNode("td", _hoisted_26$9, [createBaseVNode("span", { class: normalizeClass(["px-1.5 py-0.5 text-[10px] font-medium rounded-full", coupon.is_active ? "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400" : "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400"]) }, toDisplayString(coupon.is_active ? "Active" : "Inactive"), 3)]),
				createBaseVNode("td", _hoisted_27$8, [createBaseVNode("div", _hoisted_28$8, [createBaseVNode("button", {
					onClick: withModifiers(($event) => $setup.openEditModal(coupon), ["stop"]),
					class: "p-1 hover:bg-blue-100 dark:hover:bg-blue-600 rounded transition-colors",
					title: "Edit"
				}, [..._cache[29] || (_cache[29] = [createBaseVNode("svg", {
					class: "w-3.5 h-3.5 text-blue-600 dark:text-blue-400",
					fill: "none",
					stroke: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", {
					"stroke-linecap": "round",
					"stroke-linejoin": "round",
					"stroke-width": "2",
					d: "M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
				})], -1)])], 8, _hoisted_29$8), createBaseVNode("button", {
					onClick: withModifiers(($event) => $setup.openDeleteModal(coupon), ["stop"]),
					class: "p-1 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors",
					title: "Delete"
				}, [..._cache[30] || (_cache[30] = [createBaseVNode("svg", {
					class: "w-3.5 h-3.5 text-red-600 dark:text-red-400",
					fill: "none",
					stroke: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", {
					"stroke-linecap": "round",
					"stroke-linejoin": "round",
					"stroke-width": "2",
					d: "M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
				})], -1)])], 8, _hoisted_30$8)])])
			], 8, _hoisted_16$10);
		}), 128))])])])])]),
		$setup.showFormModal ? (openBlock(), createElementBlock("div", {
			key: 1,
			class: "fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4",
			onClick: _cache[17] || (_cache[17] = withModifiers((...args) => $setup.closeFormModal && $setup.closeFormModal(...args), ["self"]))
		}, [createBaseVNode("div", _hoisted_31$8, [
			createBaseVNode("div", _hoisted_32$8, [createBaseVNode("h2", _hoisted_33$8, toDisplayString($setup.selectedCoupon?.id ? "Edit Coupon" : "Add Coupon"), 1), createBaseVNode("button", {
				onClick: _cache[5] || (_cache[5] = (...args) => $setup.closeFormModal && $setup.closeFormModal(...args)),
				class: "p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
			}, [..._cache[32] || (_cache[32] = [createBaseVNode("svg", {
				class: "w-4 h-4",
				fill: "none",
				stroke: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M6 18L18 6M6 6l12 12"
			})], -1)])])]),
			createBaseVNode("div", _hoisted_34$8, [createBaseVNode("div", _hoisted_35$8, [
				createBaseVNode("div", null, [_cache[33] || (_cache[33] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Code *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => $setup.formData.code = $event),
					type: "text",
					required: "",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.code]])]),
				createBaseVNode("div", null, [_cache[34] || (_cache[34] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Name *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => $setup.formData.name = $event),
					type: "text",
					required: "",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.name]])]),
				createBaseVNode("div", null, [_cache[36] || (_cache[36] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Type *", -1)), withDirectives(createBaseVNode("select", {
					"onUpdate:modelValue": _cache[8] || (_cache[8] = ($event) => $setup.formData.coupon_type = $event),
					required: "",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, [..._cache[35] || (_cache[35] = [
					createBaseVNode("option", { value: "percentage" }, "Percentage", -1),
					createBaseVNode("option", { value: "fixed" }, "Fixed Amount", -1),
					createBaseVNode("option", { value: "package" }, "Package Upgrade", -1)
				])], 512), [[vModelSelect, $setup.formData.coupon_type]])]),
				createBaseVNode("div", null, [_cache[37] || (_cache[37] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Discount Value *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[9] || (_cache[9] = ($event) => $setup.formData.discount_value = $event),
					type: "number",
					step: "0.01",
					required: "",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.discount_value]])]),
				createBaseVNode("div", null, [_cache[38] || (_cache[38] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Max Uses", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[10] || (_cache[10] = ($event) => $setup.formData.max_uses = $event),
					type: "number",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.max_uses]])]),
				createBaseVNode("div", null, [_cache[39] || (_cache[39] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Valid Until", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[11] || (_cache[11] = ($event) => $setup.formData.valid_until = $event),
					type: "datetime-local",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.valid_until]])]),
				createBaseVNode("div", _hoisted_36$8, [createBaseVNode("label", _hoisted_37$8, [withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[12] || (_cache[12] = ($event) => $setup.formData.is_active = $event),
					type: "checkbox",
					class: "w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded"
				}, null, 512), [[vModelCheckbox, $setup.formData.is_active]]), _cache[40] || (_cache[40] = createBaseVNode("span", { class: "text-xs text-slate-700 dark:text-slate-300" }, "Active", -1))])]),
				createBaseVNode("div", _hoisted_38$8, [createBaseVNode("label", _hoisted_39$8, [withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[13] || (_cache[13] = ($event) => $setup.formData.is_reward = $event),
					type: "checkbox",
					class: "w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded"
				}, null, 512), [[vModelCheckbox, $setup.formData.is_reward]]), _cache[41] || (_cache[41] = createBaseVNode("span", { class: "text-xs text-slate-700 dark:text-slate-300" }, "Reward Coupon", -1))])]),
				createBaseVNode("div", _hoisted_40$8, [_cache[42] || (_cache[42] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Description", -1)), withDirectives(createBaseVNode("textarea", {
					"onUpdate:modelValue": _cache[14] || (_cache[14] = ($event) => $setup.formData.description = $event),
					rows: "3",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.description]])])
			])]),
			createBaseVNode("div", _hoisted_41$8, [createBaseVNode("button", {
				onClick: _cache[15] || (_cache[15] = (...args) => $setup.closeFormModal && $setup.closeFormModal(...args)),
				class: "px-3 py-2 text-xs bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg"
			}, "Cancel"), createBaseVNode("button", {
				onClick: _cache[16] || (_cache[16] = (...args) => $setup.saveCoupon && $setup.saveCoupon(...args)),
				disabled: $setup.saveLoading,
				class: normalizeClass(["px-3 py-2 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-lg", { "opacity-50": $setup.saveLoading }])
			}, toDisplayString($setup.saveLoading ? "Saving..." : $setup.selectedCoupon?.id ? "Update" : "Create"), 11, _hoisted_42$7)])
		])])) : createCommentVNode("", true),
		createVNode(_component_ConfirmDialog, {
			show: $setup.showDeleteModal,
			title: "Delete Coupon",
			message: `Delete coupon ${$setup.couponToDelete?.code}?`,
			type: "danger",
			onConfirm: $setup.confirmDelete,
			onCancel: $setup.closeDeleteModal
		}, null, 8, [
			"show",
			"message",
			"onConfirm",
			"onCancel"
		])
	]);
}
var Coupons_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$14, [["render", _sfc_render$14], ["__scopeId", "data-v-1315c992"]]);
var _sfc_main$13 = {
	name: "Promotions",
	components: {
		ModernMetricCard: MetricCard_default,
		ConfirmDialog: ConfirmDialog_default
	},
	setup() {
		const { loading, error, makeRequest } = useApi();
		const promotions = ref([]);
		const stats = ref({});
		const searchTerm = ref("");
		const statusFilter = ref("");
		const showFormModal = ref(false);
		const showDeleteModal = ref(false);
		const selectedPromotion = ref(null);
		const promotionToDelete = ref(null);
		const saveLoading = ref(false);
		const formData = ref({
			name: "",
			promotion_type: "featured_coupon",
			package: "",
			headline: "",
			start_date: "",
			end_date: "",
			display_order: 0,
			is_active: true,
			description: ""
		});
		const filteredPromotions = computed(() => {
			let result = promotions.value;
			if (searchTerm.value) {
				const term = searchTerm.value.toLowerCase();
				result = result.filter((p) => p.name?.toLowerCase().includes(term) || p.headline?.toLowerCase().includes(term));
			}
			if (statusFilter.value) result = result.filter((p) => p.is_active === (statusFilter.value === "true"));
			return result;
		});
		const fetchPromotions = async () => {
			try {
				const data = await makeRequest("get", "suapi/promotions/");
				promotions.value = data.results || data;
			} catch (err) {
				console.error("Error:", err);
			}
		};
		const fetchStats = async () => {
			try {
				stats.value = await makeRequest("get", "suapi/promotions/stats/");
			} catch (err) {
				console.error("Error:", err);
			}
		};
		const refreshData = () => Promise.all([fetchPromotions(), fetchStats()]);
		const formatDate = (date) => date ? new Date(date).toLocaleDateString() : "N/A";
		const openAddModal = () => {
			selectedPromotion.value = null;
			formData.value = {
				name: "",
				promotion_type: "featured_coupon",
				package: "",
				headline: "",
				start_date: "",
				end_date: "",
				display_order: 0,
				is_active: true,
				description: ""
			};
			showFormModal.value = true;
		};
		const openEditModal = (promo) => {
			selectedPromotion.value = promo;
			formData.value = {
				name: promo.name || "",
				promotion_type: promo.promotion_type || "featured_coupon",
				package: promo.package || "",
				headline: promo.headline || "",
				start_date: promo.start_date || "",
				end_date: promo.end_date || "",
				display_order: promo.display_order || 0,
				is_active: promo.is_active || false,
				description: promo.description || ""
			};
			showFormModal.value = true;
		};
		const closeFormModal = () => {
			showFormModal.value = false;
			selectedPromotion.value = null;
			formData.value = {
				name: "",
				promotion_type: "featured_coupon",
				package: "",
				headline: "",
				start_date: "",
				end_date: "",
				display_order: 0,
				is_active: true,
				description: ""
			};
		};
		const savePromotion = async () => {
			saveLoading.value = true;
			try {
				if (selectedPromotion.value?.id) await makeRequest("patch", `suapi/promotions/${selectedPromotion.value.id}/`, formData.value);
				else await makeRequest("post", "suapi/promotions/", formData.value);
				await refreshData();
				closeFormModal();
			} catch (err) {
				alert("Error: " + (err.response?.data?.error || JSON.stringify(err.response?.data) || err.message));
			} finally {
				saveLoading.value = false;
			}
		};
		const openDeleteModal = (promo) => {
			promotionToDelete.value = promo;
			showDeleteModal.value = true;
		};
		const closeDeleteModal = () => {
			showDeleteModal.value = false;
			promotionToDelete.value = null;
		};
		const confirmDelete = async () => {
			try {
				await makeRequest("delete", `suapi/promotions/${promotionToDelete.value.id}/`);
				await refreshData();
				closeDeleteModal();
			} catch (err) {
				alert("Error: " + (err.response?.data?.error || err.message));
			}
		};
		onMounted(refreshData);
		return {
			loading,
			error,
			promotions,
			stats,
			searchTerm,
			statusFilter,
			showFormModal,
			showDeleteModal,
			selectedPromotion,
			promotionToDelete,
			saveLoading,
			formData,
			filteredPromotions,
			fetchPromotions,
			refreshData,
			formatDate,
			openAddModal,
			openEditModal,
			closeFormModal,
			savePromotion,
			openDeleteModal,
			closeDeleteModal,
			confirmDelete
		};
	}
};
var _hoisted_1$13 = { class: "space-y-4 animate-fade-in" };
var _hoisted_2$13 = { class: "flex items-center justify-between" };
var _hoisted_3$13 = { class: "flex items-center gap-2" };
var _hoisted_4$13 = {
	key: 0,
	class: "bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-lg p-4"
};
var _hoisted_5$13 = { class: "flex items-center justify-between" };
var _hoisted_6$13 = { class: "flex items-center gap-3" };
var _hoisted_7$13 = { class: "text-xs text-rose-600 dark:text-rose-500 mt-1" };
var _hoisted_8$13 = { class: "grid grid-cols-2 md:grid-cols-4 gap-3 animate-slide-up" };
var _hoisted_9$11 = {
	class: "space-y-3 animate-slide-up",
	style: { "animation-delay": "0.1s" }
};
var _hoisted_10$10 = { class: "flex items-center gap-2" };
var _hoisted_11$9 = { class: "flex-1" };
var _hoisted_12$9 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden" };
var _hoisted_13$9 = { class: "overflow-x-auto" };
var _hoisted_14$9 = { class: "w-full" };
var _hoisted_15$9 = { class: "divide-y divide-slate-200 dark:divide-slate-700" };
var _hoisted_16$9 = ["onClick"];
var _hoisted_17$9 = { class: "px-3 py-2" };
var _hoisted_18$9 = { class: "flex items-center gap-2" };
var _hoisted_19$8 = { class: "text-xs font-medium text-slate-900 dark:text-white" };
var _hoisted_20$8 = { class: "text-[10px] text-slate-500 dark:text-slate-400" };
var _hoisted_21$8 = { class: "px-3 py-2" };
var _hoisted_22$8 = { class: "px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400" };
var _hoisted_23$8 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white" };
var _hoisted_24$8 = { class: "px-3 py-2" };
var _hoisted_25$8 = { class: "text-[10px] text-slate-900 dark:text-white" };
var _hoisted_26$8 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white" };
var _hoisted_27$7 = { class: "text-[10px]" };
var _hoisted_28$7 = { class: "px-3 py-2" };
var _hoisted_29$7 = { class: "px-3 py-2 text-right" };
var _hoisted_30$7 = { class: "flex items-center justify-end gap-0.5" };
var _hoisted_31$7 = ["onClick"];
var _hoisted_32$7 = ["onClick"];
var _hoisted_33$7 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden" };
var _hoisted_34$7 = { class: "flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700" };
var _hoisted_35$7 = { class: "text-base font-semibold text-slate-900 dark:text-white" };
var _hoisted_36$7 = { class: "p-5 overflow-y-auto max-h-[calc(90vh-140px)]" };
var _hoisted_37$7 = { class: "grid grid-cols-2 gap-4" };
var _hoisted_38$7 = { class: "col-span-2" };
var _hoisted_39$7 = { class: "col-span-2" };
var _hoisted_40$7 = { class: "flex items-center" };
var _hoisted_41$7 = { class: "flex items-center gap-2 cursor-pointer" };
var _hoisted_42$6 = { class: "col-span-2" };
var _hoisted_43$6 = { class: "flex items-center justify-end gap-2 p-5 border-t border-slate-200 dark:border-slate-700" };
var _hoisted_44$6 = ["disabled"];
function _sfc_render$13(_ctx, _cache, $props, $setup, $data, $options) {
	const _component_ModernMetricCard = resolveComponent("ModernMetricCard");
	const _component_ConfirmDialog = resolveComponent("ConfirmDialog");
	return openBlock(), createElementBlock("div", _hoisted_1$13, [
		createBaseVNode("div", _hoisted_2$13, [_cache[20] || (_cache[20] = createBaseVNode("div", null, [createBaseVNode("h1", { class: "text-lg font-semibold text-slate-900 dark:text-white" }, "Promotions"), createBaseVNode("p", { class: "text-xs text-slate-500 dark:text-slate-400 mt-0.5" }, "Manage featured promotions")], -1)), createBaseVNode("div", _hoisted_3$13, [createBaseVNode("button", {
			onClick: _cache[0] || (_cache[0] = (...args) => $setup.openAddModal && $setup.openAddModal(...args)),
			class: "px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-xs flex items-center gap-1.5"
		}, [..._cache[18] || (_cache[18] = [createBaseVNode("svg", {
			class: "w-3.5 h-3.5",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M12 4v16m8-8H4"
		})], -1), createTextVNode(" Add Promotion ", -1)])]), createBaseVNode("button", {
			onClick: _cache[1] || (_cache[1] = (...args) => $setup.refreshData && $setup.refreshData(...args)),
			class: normalizeClass(["p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors", { "animate-spin": $setup.loading }])
		}, [..._cache[19] || (_cache[19] = [createBaseVNode("svg", {
			class: "w-4 h-4 text-slate-600 dark:text-slate-400",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
		})], -1)])], 2)])]),
		$setup.error ? (openBlock(), createElementBlock("div", _hoisted_4$13, [createBaseVNode("div", _hoisted_5$13, [createBaseVNode("div", _hoisted_6$13, [_cache[22] || (_cache[22] = createBaseVNode("svg", {
			class: "w-5 h-5 text-rose-600 dark:text-rose-400",
			fill: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" })], -1)), createBaseVNode("div", null, [_cache[21] || (_cache[21] = createBaseVNode("h3", { class: "text-sm font-medium text-rose-800 dark:text-rose-400" }, "Failed to load promotions", -1)), createBaseVNode("p", _hoisted_7$13, toDisplayString($setup.error), 1)])]), createBaseVNode("button", {
			onClick: _cache[2] || (_cache[2] = (...args) => $setup.fetchPromotions && $setup.fetchPromotions(...args)),
			class: "px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm"
		}, "Retry")])])) : createCommentVNode("", true),
		createBaseVNode("div", _hoisted_8$13, [
			createVNode(_component_ModernMetricCard, {
				title: "Total",
				value: $setup.stats.total_promotions,
				color: "blue"
			}, {
				default: withCtx(() => [..._cache[23] || (_cache[23] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Active",
				value: $setup.stats.active_promotions,
				color: "emerald"
			}, {
				default: withCtx(() => [..._cache[24] || (_cache[24] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Views",
				value: $setup.stats.total_views,
				color: "purple"
			}, {
				default: withCtx(() => [..._cache[25] || (_cache[25] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Conversions",
				value: $setup.stats.total_conversions,
				color: "amber"
			}, {
				default: withCtx(() => [..._cache[26] || (_cache[26] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" })], -1)])]),
				_: 1
			}, 8, ["value"])
		]),
		createBaseVNode("div", _hoisted_9$11, [createBaseVNode("div", _hoisted_10$10, [createBaseVNode("div", _hoisted_11$9, [withDirectives(createBaseVNode("input", {
			"onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => $setup.searchTerm = $event),
			type: "text",
			placeholder: "Search promotions...",
			class: "w-full px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs"
		}, null, 512), [[vModelText, $setup.searchTerm]])]), withDirectives(createBaseVNode("select", {
			"onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => $setup.statusFilter = $event),
			class: "px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs"
		}, [..._cache[27] || (_cache[27] = [
			createBaseVNode("option", { value: "" }, "All Status", -1),
			createBaseVNode("option", { value: "true" }, "Active", -1),
			createBaseVNode("option", { value: "false" }, "Inactive", -1)
		])], 512), [[vModelSelect, $setup.statusFilter]])]), createBaseVNode("div", _hoisted_12$9, [createBaseVNode("div", _hoisted_13$9, [createBaseVNode("table", _hoisted_14$9, [_cache[31] || (_cache[31] = createBaseVNode("thead", { class: "bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700" }, [createBaseVNode("tr", null, [
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Promotion"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Type"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Package"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Performance"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Period"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Status"),
			createBaseVNode("th", { class: "px-3 py-2 text-right text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Actions")
		])], -1)), createBaseVNode("tbody", _hoisted_15$9, [(openBlock(true), createElementBlock(Fragment, null, renderList($setup.filteredPromotions, (promo) => {
			return openBlock(), createElementBlock("tr", {
				key: promo.id,
				onClick: ($event) => $setup.openEditModal(promo),
				class: "hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer"
			}, [
				createBaseVNode("td", _hoisted_17$9, [createBaseVNode("div", _hoisted_18$9, [_cache[28] || (_cache[28] = createBaseVNode("div", { class: "w-7 h-7 rounded-lg bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center" }, [createBaseVNode("svg", {
					class: "w-4 h-4 text-white",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" })])], -1)), createBaseVNode("div", null, [createBaseVNode("p", _hoisted_19$8, toDisplayString(promo.name), 1), createBaseVNode("p", _hoisted_20$8, toDisplayString(promo.headline), 1)])])]),
				createBaseVNode("td", _hoisted_21$8, [createBaseVNode("span", _hoisted_22$8, toDisplayString(promo.promotion_type), 1)]),
				createBaseVNode("td", _hoisted_23$8, toDisplayString(promo.package_name || "N/A"), 1),
				createBaseVNode("td", _hoisted_24$8, [createBaseVNode("div", _hoisted_25$8, [
					createBaseVNode("div", null, "Views: " + toDisplayString(promo.views || 0), 1),
					createBaseVNode("div", null, "Clicks: " + toDisplayString(promo.clicks || 0), 1),
					createBaseVNode("div", null, "Conv: " + toDisplayString(promo.conversions || 0), 1)
				])]),
				createBaseVNode("td", _hoisted_26$8, [createBaseVNode("div", _hoisted_27$7, [createBaseVNode("div", null, toDisplayString($setup.formatDate(promo.start_date)), 1), createBaseVNode("div", null, toDisplayString($setup.formatDate(promo.end_date)), 1)])]),
				createBaseVNode("td", _hoisted_28$7, [createBaseVNode("span", { class: normalizeClass(["px-1.5 py-0.5 text-[10px] font-medium rounded-full", promo.is_active ? "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400" : "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400"]) }, toDisplayString(promo.is_active ? "Active" : "Inactive"), 3)]),
				createBaseVNode("td", _hoisted_29$7, [createBaseVNode("div", _hoisted_30$7, [createBaseVNode("button", {
					onClick: withModifiers(($event) => $setup.openEditModal(promo), ["stop"]),
					class: "p-1 hover:bg-blue-100 dark:hover:bg-blue-600 rounded transition-colors",
					title: "Edit"
				}, [..._cache[29] || (_cache[29] = [createBaseVNode("svg", {
					class: "w-3.5 h-3.5 text-blue-600 dark:text-blue-400",
					fill: "none",
					stroke: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", {
					"stroke-linecap": "round",
					"stroke-linejoin": "round",
					"stroke-width": "2",
					d: "M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
				})], -1)])], 8, _hoisted_31$7), createBaseVNode("button", {
					onClick: withModifiers(($event) => $setup.openDeleteModal(promo), ["stop"]),
					class: "p-1 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors",
					title: "Delete"
				}, [..._cache[30] || (_cache[30] = [createBaseVNode("svg", {
					class: "w-3.5 h-3.5 text-red-600 dark:text-red-400",
					fill: "none",
					stroke: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", {
					"stroke-linecap": "round",
					"stroke-linejoin": "round",
					"stroke-width": "2",
					d: "M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
				})], -1)])], 8, _hoisted_32$7)])])
			], 8, _hoisted_16$9);
		}), 128))])])])])]),
		$setup.showFormModal ? (openBlock(), createElementBlock("div", {
			key: 1,
			class: "fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4",
			onClick: _cache[17] || (_cache[17] = withModifiers((...args) => $setup.closeFormModal && $setup.closeFormModal(...args), ["self"]))
		}, [createBaseVNode("div", _hoisted_33$7, [
			createBaseVNode("div", _hoisted_34$7, [createBaseVNode("h2", _hoisted_35$7, toDisplayString($setup.selectedPromotion?.id ? "Edit Promotion" : "Add Promotion"), 1), createBaseVNode("button", {
				onClick: _cache[5] || (_cache[5] = (...args) => $setup.closeFormModal && $setup.closeFormModal(...args)),
				class: "p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
			}, [..._cache[32] || (_cache[32] = [createBaseVNode("svg", {
				class: "w-4 h-4",
				fill: "none",
				stroke: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M6 18L18 6M6 6l12 12"
			})], -1)])])]),
			createBaseVNode("div", _hoisted_36$7, [createBaseVNode("div", _hoisted_37$7, [
				createBaseVNode("div", _hoisted_38$7, [_cache[33] || (_cache[33] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Name *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => $setup.formData.name = $event),
					type: "text",
					required: "",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.name]])]),
				createBaseVNode("div", null, [_cache[35] || (_cache[35] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Type *", -1)), withDirectives(createBaseVNode("select", {
					"onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => $setup.formData.promotion_type = $event),
					required: "",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, [..._cache[34] || (_cache[34] = [createStaticVNode("<option value=\"featured_coupon\" data-v-e68cb6b5>Featured with Coupon</option><option value=\"bundle\" data-v-e68cb6b5>Bundle</option><option value=\"seasonal\" data-v-e68cb6b5>Seasonal</option><option value=\"flash_sale\" data-v-e68cb6b5>Flash Sale</option><option value=\"new_arrival\" data-v-e68cb6b5>New Arrival</option><option value=\"best_seller\" data-v-e68cb6b5>Best Seller</option>", 6)])], 512), [[vModelSelect, $setup.formData.promotion_type]])]),
				createBaseVNode("div", null, [_cache[36] || (_cache[36] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Package ID *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[8] || (_cache[8] = ($event) => $setup.formData.package = $event),
					type: "number",
					required: "",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.package]])]),
				createBaseVNode("div", _hoisted_39$7, [_cache[37] || (_cache[37] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Headline *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[9] || (_cache[9] = ($event) => $setup.formData.headline = $event),
					type: "text",
					required: "",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.headline]])]),
				createBaseVNode("div", null, [_cache[38] || (_cache[38] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Start Date *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[10] || (_cache[10] = ($event) => $setup.formData.start_date = $event),
					type: "datetime-local",
					required: "",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.start_date]])]),
				createBaseVNode("div", null, [_cache[39] || (_cache[39] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "End Date *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[11] || (_cache[11] = ($event) => $setup.formData.end_date = $event),
					type: "datetime-local",
					required: "",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.end_date]])]),
				createBaseVNode("div", null, [_cache[40] || (_cache[40] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Display Order", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[12] || (_cache[12] = ($event) => $setup.formData.display_order = $event),
					type: "number",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.display_order]])]),
				createBaseVNode("div", _hoisted_40$7, [createBaseVNode("label", _hoisted_41$7, [withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[13] || (_cache[13] = ($event) => $setup.formData.is_active = $event),
					type: "checkbox",
					class: "w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded"
				}, null, 512), [[vModelCheckbox, $setup.formData.is_active]]), _cache[41] || (_cache[41] = createBaseVNode("span", { class: "text-xs text-slate-700 dark:text-slate-300" }, "Active", -1))])]),
				createBaseVNode("div", _hoisted_42$6, [_cache[42] || (_cache[42] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Description", -1)), withDirectives(createBaseVNode("textarea", {
					"onUpdate:modelValue": _cache[14] || (_cache[14] = ($event) => $setup.formData.description = $event),
					rows: "3",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.description]])])
			])]),
			createBaseVNode("div", _hoisted_43$6, [createBaseVNode("button", {
				onClick: _cache[15] || (_cache[15] = (...args) => $setup.closeFormModal && $setup.closeFormModal(...args)),
				class: "px-3 py-2 text-xs bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg"
			}, "Cancel"), createBaseVNode("button", {
				onClick: _cache[16] || (_cache[16] = (...args) => $setup.savePromotion && $setup.savePromotion(...args)),
				disabled: $setup.saveLoading,
				class: normalizeClass(["px-3 py-2 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-lg", { "opacity-50": $setup.saveLoading }])
			}, toDisplayString($setup.saveLoading ? "Saving..." : $setup.selectedPromotion?.id ? "Update" : "Create"), 11, _hoisted_44$6)])
		])])) : createCommentVNode("", true),
		createVNode(_component_ConfirmDialog, {
			show: $setup.showDeleteModal,
			title: "Delete Promotion",
			message: `Delete promotion ${$setup.promotionToDelete?.name}?`,
			type: "danger",
			onConfirm: $setup.confirmDelete,
			onCancel: $setup.closeDeleteModal
		}, null, 8, [
			"show",
			"message",
			"onConfirm",
			"onCancel"
		])
	]);
}
var Promotions_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$13, [["render", _sfc_render$13], ["__scopeId", "data-v-e68cb6b5"]]);
var _sfc_main$12 = {
	name: "SearchBar",
	components: {
		MagnifyingGlassIcon: render$17,
		PlusIcon: render$18,
		ArrowPathIcon: render$9
	},
	props: {
		modelValue: {
			type: String,
			default: ""
		},
		placeholder: {
			type: String,
			default: "Search..."
		},
		filters: {
			type: Array,
			default: () => []
		},
		showAddButton: {
			type: Boolean,
			default: true
		},
		addButtonText: {
			type: String,
			default: "Add New"
		}
	},
	emits: [
		"update:modelValue",
		"filter-change",
		"clear",
		"add"
	],
	setup(props, { emit }) {
		const filterValues = ref({});
		watch(() => props.filters, (newFilters) => {
			newFilters.forEach((filter) => {
				if (filterValues.value[filter.key] === void 0) filterValues.value[filter.key] = "";
			});
		}, { immediate: true });
		const handleFilterChange = (key, value) => {
			filterValues.value[key] = value;
			emit("filter-change", {
				key,
				value,
				all: filterValues.value
			});
		};
		return {
			filterValues,
			handleFilterChange
		};
	}
};
var _hoisted_1$12 = { class: "bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-4 transition-all duration-300" };
var _hoisted_2$12 = { class: "flex flex-col lg:flex-row lg:items-center gap-3" };
var _hoisted_3$12 = { class: "flex-1 relative group" };
var _hoisted_4$12 = ["value", "placeholder"];
var _hoisted_5$12 = {
	key: 0,
	class: "flex items-center gap-2"
};
var _hoisted_6$12 = ["value", "onChange"];
var _hoisted_7$12 = { value: "" };
var _hoisted_8$12 = ["value"];
var _hoisted_9$10 = { class: "flex gap-2" };
function _sfc_render$12(_ctx, _cache, $props, $setup, $data, $options) {
	const _component_MagnifyingGlassIcon = resolveComponent("MagnifyingGlassIcon");
	const _component_ArrowPathIcon = resolveComponent("ArrowPathIcon");
	const _component_PlusIcon = resolveComponent("PlusIcon");
	return openBlock(), createElementBlock("div", _hoisted_1$12, [createBaseVNode("div", _hoisted_2$12, [
		createBaseVNode("div", _hoisted_3$12, [createVNode(_component_MagnifyingGlassIcon, { class: "w-4 h-4 text-slate-400 dark:text-slate-500 absolute left-3 top-1/2 transform -translate-y-1/2 transition-colors group-focus-within:text-blue-500" }), createBaseVNode("input", {
			value: $props.modelValue,
			onInput: _cache[0] || (_cache[0] = ($event) => _ctx.$emit("update:modelValue", $event.target.value)),
			type: "text",
			placeholder: $props.placeholder,
			class: "w-full pl-10 pr-4 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 transition-all duration-200 text-sm"
		}, null, 40, _hoisted_4$12)]),
		$props.filters && $props.filters.length > 0 ? (openBlock(), createElementBlock("div", _hoisted_5$12, [(openBlock(true), createElementBlock(Fragment, null, renderList($props.filters, (filter) => {
			return openBlock(), createElementBlock("select", {
				key: filter.key,
				value: $setup.filterValues[filter.key],
				onChange: ($event) => $setup.handleFilterChange(filter.key, $event.target.value),
				class: "px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg focus:ring-2 focus:ring-blue-500 text-slate-900 dark:text-white text-sm transition-all duration-200"
			}, [createBaseVNode("option", _hoisted_7$12, toDisplayString(filter.label), 1), (openBlock(true), createElementBlock(Fragment, null, renderList(filter.options, (option) => {
				return openBlock(), createElementBlock("option", {
					key: option.value,
					value: option.value
				}, toDisplayString(option.label), 9, _hoisted_8$12);
			}), 128))], 40, _hoisted_6$12);
		}), 128))])) : createCommentVNode("", true),
		createBaseVNode("div", _hoisted_9$10, [createBaseVNode("button", {
			onClick: _cache[1] || (_cache[1] = ($event) => _ctx.$emit("clear")),
			class: "px-3 py-2 border border-slate-300 dark:border-slate-600 text-slate-600 dark:text-slate-400 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-all duration-200 flex items-center gap-2 text-sm"
		}, [createVNode(_component_ArrowPathIcon, { class: "w-4 h-4" }), _cache[3] || (_cache[3] = createBaseVNode("span", { class: "hidden sm:inline" }, "Clear", -1))]), $props.showAddButton ? (openBlock(), createElementBlock("button", {
			key: 0,
			onClick: _cache[2] || (_cache[2] = ($event) => _ctx.$emit("add")),
			class: "px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-all duration-200 flex items-center gap-2 shadow-sm hover:shadow text-sm"
		}, [createVNode(_component_PlusIcon, { class: "w-4 h-4" }), createBaseVNode("span", null, toDisplayString($props.addButtonText), 1)])) : createCommentVNode("", true)])
	])]);
}
var SearchBar_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$12, [["render", _sfc_render$12]]);
var _sfc_main$11 = {
	name: "DataTable",
	components: {
		PencilSquareIcon: render$10,
		TrashIcon: render$11,
		ChevronLeftIcon: render$12,
		ChevronRightIcon: render$13,
		ChevronUpDownIcon: render$14,
		ArrowDownTrayIcon: render$15
	},
	props: {
		title: {
			type: String,
			required: true
		},
		data: {
			type: Array,
			required: true
		},
		columns: {
			type: Array,
			required: true
		},
		actions: {
			type: Array,
			default: () => ["edit", "delete"]
		},
		icon: {
			type: Object,
			default: () => render$16
		},
		emptyIcon: {
			type: Object,
			default: () => render$16
		},
		emptyMessage: {
			type: String,
			default: "No data found"
		},
		emptyDescription: {
			type: String,
			default: "No records match your criteria."
		},
		exportable: {
			type: Boolean,
			default: true
		}
	},
	emits: ["edit", "delete"],
	setup(props) {
		const currentPage = ref(1);
		const itemsPerPage = ref(10);
		const sortKey = ref("");
		const sortOrder = ref("asc");
		const filteredData = computed(() => props.data);
		const sortedData = computed(() => {
			if (!sortKey.value) return filteredData.value;
			return [...filteredData.value].sort((a, b) => {
				const aVal = getNestedValue(a, sortKey.value);
				const bVal = getNestedValue(b, sortKey.value);
				if (aVal < bVal) return sortOrder.value === "asc" ? -1 : 1;
				if (aVal > bVal) return sortOrder.value === "asc" ? 1 : -1;
				return 0;
			});
		});
		const totalPages = computed(() => Math.ceil(sortedData.value.length / itemsPerPage.value));
		const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage.value);
		const endIndex = computed(() => Math.min(startIndex.value + itemsPerPage.value, sortedData.value.length));
		const paginatedData = computed(() => sortedData.value.slice(startIndex.value, endIndex.value));
		const getNestedValue = (obj, path) => {
			return path.split(".").reduce((acc, part) => acc?.[part], obj);
		};
		const formatValue = (item, column) => {
			const value = getNestedValue(item, column.key);
			if (column.format) return column.format(value, item);
			return value ?? "N/A";
		};
		const sortBy = (key) => {
			if (sortKey.value === key) sortOrder.value = sortOrder.value === "asc" ? "desc" : "asc";
			else {
				sortKey.value = key;
				sortOrder.value = "asc";
			}
		};
		const nextPage = () => {
			if (currentPage.value < totalPages.value) currentPage.value++;
		};
		const previousPage = () => {
			if (currentPage.value > 1) currentPage.value--;
		};
		const handleItemsPerPageChange = () => {
			currentPage.value = 1;
		};
		const exportToCSV = () => {
			const csv = [props.columns.map((col) => col.label).join(","), ...filteredData.value.map((item) => props.columns.map((col) => {
				return `"${getNestedValue(item, col.key) ?? ""}"`;
			}).join(","))].join("\n");
			const blob = new Blob([csv], { type: "text/csv" });
			const url = window.URL.createObjectURL(blob);
			const link = document.createElement("a");
			link.href = url;
			link.download = `${props.title.toLowerCase().replace(/\s+/g, "_")}_${(/* @__PURE__ */ new Date()).toISOString().split("T")[0]}.csv`;
			link.click();
			window.URL.revokeObjectURL(url);
		};
		return {
			currentPage,
			itemsPerPage,
			filteredData,
			paginatedData,
			totalPages,
			startIndex,
			endIndex,
			getNestedValue,
			formatValue,
			sortBy,
			nextPage,
			previousPage,
			handleItemsPerPageChange,
			exportToCSV
		};
	}
};
var _hoisted_1$11 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden transition-colors duration-300" };
var _hoisted_2$11 = { class: "px-5 py-4 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between" };
var _hoisted_3$11 = { class: "flex items-center space-x-4" };
var _hoisted_4$11 = { class: "text-base font-semibold text-slate-900 dark:text-white flex items-center" };
var _hoisted_5$11 = { class: "text-slate-500 dark:text-slate-400 font-normal ml-2" };
var _hoisted_6$11 = { class: "flex items-center space-x-2" };
var _hoisted_7$11 = { class: "overflow-x-auto" };
var _hoisted_8$11 = { class: "w-full" };
var _hoisted_9$9 = { class: "bg-slate-50 dark:bg-slate-900/50 border-b border-slate-200 dark:border-slate-700" };
var _hoisted_10$9 = ["onClick"];
var _hoisted_11$8 = { class: "flex items-center space-x-1" };
var _hoisted_12$8 = {
	key: 0,
	class: "px-5 py-3 text-left text-xs font-medium text-slate-600 dark:text-slate-400 uppercase tracking-wide"
};
var _hoisted_13$8 = { class: "divide-y divide-slate-200 dark:divide-slate-700" };
var _hoisted_14$8 = {
	key: 0,
	class: "px-5 py-3 whitespace-nowrap text-sm font-medium"
};
var _hoisted_15$8 = { class: "flex space-x-2" };
var _hoisted_16$8 = ["onClick"];
var _hoisted_17$8 = ["onClick"];
var _hoisted_18$8 = {
	key: 0,
	class: "text-center py-12"
};
var _hoisted_19$7 = { class: "w-14 h-14 bg-slate-100 dark:bg-slate-800 rounded-xl flex items-center justify-center mx-auto mb-4" };
var _hoisted_20$7 = { class: "text-base font-semibold text-slate-600 dark:text-slate-400 mb-2" };
var _hoisted_21$7 = { class: "text-sm text-slate-500 dark:text-slate-500" };
var _hoisted_22$7 = {
	key: 1,
	class: "px-5 py-3 border-t border-slate-200 dark:border-slate-700 flex items-center justify-between"
};
var _hoisted_23$7 = { class: "text-xs text-slate-600 dark:text-slate-400" };
var _hoisted_24$7 = { class: "flex space-x-2" };
var _hoisted_25$7 = ["disabled"];
var _hoisted_26$7 = ["disabled"];
function _sfc_render$11(_ctx, _cache, $props, $setup, $data, $options) {
	const _component_ArrowDownTrayIcon = resolveComponent("ArrowDownTrayIcon");
	const _component_ChevronUpDownIcon = resolveComponent("ChevronUpDownIcon");
	const _component_PencilSquareIcon = resolveComponent("PencilSquareIcon");
	const _component_TrashIcon = resolveComponent("TrashIcon");
	const _component_ChevronLeftIcon = resolveComponent("ChevronLeftIcon");
	const _component_ChevronRightIcon = resolveComponent("ChevronRightIcon");
	return openBlock(), createElementBlock("div", _hoisted_1$11, [
		createBaseVNode("div", _hoisted_2$11, [createBaseVNode("div", _hoisted_3$11, [createBaseVNode("h3", _hoisted_4$11, [
			$props.icon ? (openBlock(), createBlock(resolveDynamicComponent($props.icon), {
				key: 0,
				class: "w-4 h-4 text-slate-600 dark:text-slate-400 mr-2"
			})) : createCommentVNode("", true),
			createTextVNode(" " + toDisplayString($props.title) + " ", 1),
			createBaseVNode("span", _hoisted_5$11, "(" + toDisplayString($setup.filteredData.length) + ")", 1)
		]), createBaseVNode("div", _hoisted_6$11, [_cache[6] || (_cache[6] = createBaseVNode("span", { class: "text-xs text-slate-600 dark:text-slate-400" }, "Show:", -1)), withDirectives(createBaseVNode("select", {
			"onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => $setup.itemsPerPage = $event),
			onChange: _cache[1] || (_cache[1] = (...args) => $setup.handleItemsPerPageChange && $setup.handleItemsPerPageChange(...args)),
			class: "text-xs border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white rounded-lg px-2 py-1 focus:ring-2 focus:ring-blue-500"
		}, [..._cache[5] || (_cache[5] = [createStaticVNode("<option value=\"5\">5</option><option value=\"10\">10</option><option value=\"15\">15</option><option value=\"20\">20</option><option value=\"50\">50</option>", 5)])], 544), [[vModelSelect, $setup.itemsPerPage]])])]), renderSlot(_ctx.$slots, "header-actions", {}, () => [$props.exportable ? (openBlock(), createElementBlock("button", {
			key: 0,
			onClick: _cache[2] || (_cache[2] = (...args) => $setup.exportToCSV && $setup.exportToCSV(...args)),
			class: "px-3 py-1.5 bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-600 transition-all duration-200 flex items-center space-x-2 text-xs"
		}, [createVNode(_component_ArrowDownTrayIcon, { class: "w-3.5 h-3.5" }), _cache[7] || (_cache[7] = createBaseVNode("span", null, "Export", -1))])) : createCommentVNode("", true)])]),
		createBaseVNode("div", _hoisted_7$11, [createBaseVNode("table", _hoisted_8$11, [createBaseVNode("thead", _hoisted_9$9, [createBaseVNode("tr", null, [(openBlock(true), createElementBlock(Fragment, null, renderList($props.columns, (column) => {
			return openBlock(), createElementBlock("th", {
				key: column.key,
				class: "px-5 py-3 text-left text-xs font-medium text-slate-600 dark:text-slate-400 uppercase tracking-wide cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800",
				onClick: ($event) => column.sortable !== false && $setup.sortBy(column.key)
			}, [createBaseVNode("div", _hoisted_11$8, [createBaseVNode("span", null, toDisplayString(column.label), 1), column.sortable !== false ? (openBlock(), createBlock(_component_ChevronUpDownIcon, {
				key: 0,
				class: "w-3.5 h-3.5"
			})) : createCommentVNode("", true)])], 8, _hoisted_10$9);
		}), 128)), $props.actions ? (openBlock(), createElementBlock("th", _hoisted_12$8, " Actions ")) : createCommentVNode("", true)])]), createBaseVNode("tbody", _hoisted_13$8, [(openBlock(true), createElementBlock(Fragment, null, renderList($setup.paginatedData, (item) => {
			return openBlock(), createElementBlock("tr", {
				key: item.id,
				class: "hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors duration-200"
			}, [(openBlock(true), createElementBlock(Fragment, null, renderList($props.columns, (column) => {
				return openBlock(), createElementBlock("td", {
					key: column.key,
					class: normalizeClass(["px-5 py-3 whitespace-nowrap text-sm", column.class || "text-slate-600 dark:text-slate-400"])
				}, [renderSlot(_ctx.$slots, `cell-${column.key}`, {
					item,
					value: $setup.getNestedValue(item, column.key)
				}, () => [createTextVNode(toDisplayString($setup.formatValue(item, column)), 1)])], 2);
			}), 128)), $props.actions ? (openBlock(), createElementBlock("td", _hoisted_14$8, [createBaseVNode("div", _hoisted_15$8, [
				$props.actions.includes("edit") ? (openBlock(), createElementBlock("button", {
					key: 0,
					onClick: ($event) => _ctx.$emit("edit", item),
					class: "text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 transition-colors duration-200 p-1 rounded",
					title: "Edit"
				}, [createVNode(_component_PencilSquareIcon, { class: "w-4 h-4" })], 8, _hoisted_16$8)) : createCommentVNode("", true),
				$props.actions.includes("delete") ? (openBlock(), createElementBlock("button", {
					key: 1,
					onClick: ($event) => _ctx.$emit("delete", item),
					class: "text-rose-600 dark:text-rose-400 hover:text-rose-800 dark:hover:text-rose-300 transition-colors duration-200 p-1 rounded",
					title: "Delete"
				}, [createVNode(_component_TrashIcon, { class: "w-4 h-4" })], 8, _hoisted_17$8)) : createCommentVNode("", true),
				renderSlot(_ctx.$slots, "custom-actions", { item })
			])])) : createCommentVNode("", true)]);
		}), 128))])])]),
		$setup.filteredData.length === 0 ? (openBlock(), createElementBlock("div", _hoisted_18$8, [
			createBaseVNode("div", _hoisted_19$7, [(openBlock(), createBlock(resolveDynamicComponent($props.emptyIcon), { class: "w-7 h-7 text-slate-400 dark:text-slate-500" }))]),
			createBaseVNode("h3", _hoisted_20$7, toDisplayString($props.emptyMessage), 1),
			createBaseVNode("p", _hoisted_21$7, toDisplayString($props.emptyDescription), 1)
		])) : createCommentVNode("", true),
		$setup.filteredData.length > 0 ? (openBlock(), createElementBlock("div", _hoisted_22$7, [createBaseVNode("div", _hoisted_23$7, " Showing " + toDisplayString($setup.startIndex + 1) + " to " + toDisplayString($setup.endIndex) + " of " + toDisplayString($setup.filteredData.length), 1), createBaseVNode("div", _hoisted_24$7, [createBaseVNode("button", {
			onClick: _cache[3] || (_cache[3] = (...args) => $setup.previousPage && $setup.previousPage(...args)),
			disabled: $setup.currentPage === 1,
			class: normalizeClass(["px-3 py-1.5 rounded-lg border transition-all duration-200 text-xs", $setup.currentPage === 1 ? "border-slate-300 dark:border-slate-700 text-slate-400 dark:text-slate-600 cursor-not-allowed" : "border-slate-300 dark:border-slate-600 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800"])
		}, [createVNode(_component_ChevronLeftIcon, { class: "w-4 h-4" })], 10, _hoisted_25$7), createBaseVNode("button", {
			onClick: _cache[4] || (_cache[4] = (...args) => $setup.nextPage && $setup.nextPage(...args)),
			disabled: $setup.currentPage >= $setup.totalPages,
			class: normalizeClass(["px-3 py-1.5 rounded-lg border transition-all duration-200 text-xs", $setup.currentPage >= $setup.totalPages ? "border-slate-300 dark:border-slate-700 text-slate-400 dark:text-slate-600 cursor-not-allowed" : "border-slate-300 dark:border-slate-600 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800"])
		}, [createVNode(_component_ChevronRightIcon, { class: "w-4 h-4" })], 10, _hoisted_26$7)])])) : createCommentVNode("", true)
	]);
}
var DataTable_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$11, [["render", _sfc_render$11]]);
var _sfc_main$10 = {
	name: "PointTransactions",
	components: {
		ModernMetricCard: MetricCard_default,
		SearchBar: SearchBar_default,
		DataTable: DataTable_default,
		ArrowPathIcon: render$9,
		ExclamationTriangleIcon: render$7
	},
	setup() {
		const { loading, error, makeRequest } = useApi();
		const transactions = ref([]);
		const stats = ref({});
		const searchTerm = ref("");
		const activeFilters = ref({});
		const columns = [
			{
				key: "id",
				label: "ID",
				sortable: true
			},
			{
				key: "user_username",
				label: "User",
				sortable: true
			},
			{
				key: "transaction_type",
				label: "Type",
				sortable: true
			},
			{
				key: "points",
				label: "Points",
				sortable: true
			},
			{
				key: "description",
				label: "Description",
				sortable: true
			},
			{
				key: "created_at",
				label: "Date",
				sortable: true,
				format: (v) => new Date(v).toLocaleDateString()
			}
		];
		const filters = [{
			key: "transaction_type",
			label: "Type",
			options: [{
				value: "earn",
				label: "Earned"
			}, {
				value: "redeem",
				label: "Redeemed"
			}]
		}];
		const filteredTransactions = computed(() => {
			let result = transactions.value;
			if (searchTerm.value) {
				const term = searchTerm.value.toLowerCase();
				result = result.filter((t) => t.user_username?.toLowerCase().includes(term) || t.description?.toLowerCase().includes(term));
			}
			Object.keys(activeFilters.value).forEach((key) => {
				const value = activeFilters.value[key];
				if (value) result = result.filter((t) => t[key] === value);
			});
			return result;
		});
		const fetchTransactions = async () => {
			try {
				const data = await makeRequest("get", "suapi/point-transactions/");
				transactions.value = data.results || data;
			} catch (err) {
				console.error("Error:", err);
			}
		};
		const fetchStats = async () => {
			try {
				stats.value = await makeRequest("get", "suapi/point-transactions/stats/");
			} catch (err) {
				console.error("Error:", err);
			}
		};
		const refreshData = () => Promise.all([fetchTransactions(), fetchStats()]);
		const handleFilterChange = ({ all }) => {
			activeFilters.value = all;
		};
		const clearFilters = () => {
			searchTerm.value = "";
			activeFilters.value = {};
		};
		onMounted(refreshData);
		return {
			loading,
			error,
			transactions,
			stats,
			searchTerm,
			columns,
			filters,
			filteredTransactions,
			fetchTransactions,
			refreshData,
			handleFilterChange,
			clearFilters
		};
	}
};
var _hoisted_1$10 = { class: "space-y-6 animate-fade-in" };
var _hoisted_2$10 = { class: "flex items-center justify-between" };
var _hoisted_3$10 = {
	key: 0,
	class: "bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-lg p-4"
};
var _hoisted_4$10 = { class: "flex items-center justify-between" };
var _hoisted_5$10 = { class: "flex items-center gap-3" };
var _hoisted_6$10 = { class: "text-xs text-rose-600 dark:text-rose-500 mt-1" };
var _hoisted_7$10 = { class: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-slide-up" };
var _hoisted_8$10 = {
	class: "space-y-4 animate-slide-up",
	style: { "animation-delay": "0.1s" }
};
function _sfc_render$10(_ctx, _cache, $props, $setup, $data, $options) {
	const _component_ArrowPathIcon = resolveComponent("ArrowPathIcon");
	const _component_ExclamationTriangleIcon = resolveComponent("ExclamationTriangleIcon");
	const _component_ModernMetricCard = resolveComponent("ModernMetricCard");
	const _component_SearchBar = resolveComponent("SearchBar");
	const _component_DataTable = resolveComponent("DataTable");
	return openBlock(), createElementBlock("div", _hoisted_1$10, [
		createBaseVNode("div", _hoisted_2$10, [_cache[3] || (_cache[3] = createBaseVNode("div", null, [createBaseVNode("h1", { class: "text-2xl font-semibold text-slate-900 dark:text-white" }, "Point Transactions"), createBaseVNode("p", { class: "text-sm text-slate-500 dark:text-slate-400 mt-1" }, "Track reward points activity")], -1)), createBaseVNode("button", {
			onClick: _cache[0] || (_cache[0] = (...args) => $setup.refreshData && $setup.refreshData(...args)),
			class: normalizeClass(["p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors", { "animate-spin": $setup.loading }])
		}, [createVNode(_component_ArrowPathIcon, { class: "w-5 h-5 text-slate-600 dark:text-slate-400" })], 2)]),
		$setup.error ? (openBlock(), createElementBlock("div", _hoisted_3$10, [createBaseVNode("div", _hoisted_4$10, [createBaseVNode("div", _hoisted_5$10, [createVNode(_component_ExclamationTriangleIcon, { class: "w-5 h-5 text-rose-600 dark:text-rose-400" }), createBaseVNode("div", null, [_cache[4] || (_cache[4] = createBaseVNode("h3", { class: "text-sm font-medium text-rose-800 dark:text-rose-400" }, "Failed to load transactions", -1)), createBaseVNode("p", _hoisted_6$10, toDisplayString($setup.error), 1)])]), createBaseVNode("button", {
			onClick: _cache[1] || (_cache[1] = (...args) => $setup.fetchTransactions && $setup.fetchTransactions(...args)),
			class: "px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm"
		}, "Retry")])])) : createCommentVNode("", true),
		createBaseVNode("div", _hoisted_7$10, [
			createVNode(_component_ModernMetricCard, {
				title: "Total Transactions",
				value: $setup.stats.total_transactions,
				icon: "🏆",
				color: "blue"
			}, null, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Points Earned",
				value: $setup.stats.total_earned,
				icon: "➕",
				color: "emerald"
			}, null, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Points Redeemed",
				value: $setup.stats.total_redeemed,
				icon: "➖",
				color: "rose"
			}, null, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Net Balance",
				value: $setup.stats.net_balance,
				icon: "💰",
				color: "purple"
			}, null, 8, ["value"])
		]),
		createBaseVNode("div", _hoisted_8$10, [createVNode(_component_SearchBar, {
			modelValue: $setup.searchTerm,
			"onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => $setup.searchTerm = $event),
			placeholder: "Search transactions...",
			filters: $setup.filters,
			onFilterChange: $setup.handleFilterChange,
			onClear: $setup.clearFilters,
			"show-add-button": false
		}, null, 8, [
			"modelValue",
			"filters",
			"onFilterChange",
			"onClear"
		]), createVNode(_component_DataTable, {
			title: "Transaction Records",
			data: $setup.filteredTransactions,
			columns: $setup.columns,
			actions: []
		}, {
			"cell-transaction_type": withCtx(({ value }) => [createBaseVNode("span", { class: normalizeClass([value === "earn" ? "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400" : "bg-rose-100 dark:bg-rose-500/20 text-rose-700 dark:text-rose-400", "px-2 py-0.5 text-xs font-medium rounded-full"]) }, toDisplayString(value === "earn" ? "➕ Earned" : "➖ Redeemed"), 3)]),
			"cell-points": withCtx(({ value, item }) => [createBaseVNode("span", { class: normalizeClass([item.transaction_type === "earn" ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400", "font-medium"]) }, toDisplayString(item.transaction_type === "earn" ? "+" : "-") + toDisplayString(value), 3)]),
			_: 1
		}, 8, ["data", "columns"])])
	]);
}
var PointTransactions_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$10, [["render", _sfc_render$10], ["__scopeId", "data-v-2905984b"]]);
var _sfc_main$9 = {
	name: "Locations",
	components: {
		ModernMetricCard: MetricCard_default,
		ConfirmDialog: ConfirmDialog_default
	},
	setup() {
		const { loading, error, makeRequest } = useApi();
		const locations = ref([]);
		const stats = ref({});
		const searchTerm = ref("");
		const statusFilter = ref("");
		const showFormModal = ref(false);
		const showDeleteModal = ref(false);
		const selectedLocation = ref(null);
		const locationToDelete = ref(null);
		const saveLoading = ref(false);
		const formData = ref({
			name: "",
			code: "",
			location_type: "hotspot",
			city: "",
			max_concurrent_users: 100,
			router_ip: "",
			is_active: true,
			allow_roaming_in: true,
			address: ""
		});
		const filteredLocations = computed(() => {
			let result = locations.value;
			if (searchTerm.value) {
				const term = searchTerm.value.toLowerCase();
				result = result.filter((l) => l.name?.toLowerCase().includes(term) || l.code?.toLowerCase().includes(term) || l.city?.toLowerCase().includes(term));
			}
			if (statusFilter.value) result = result.filter((l) => l.is_active === (statusFilter.value === "true"));
			return result;
		});
		const fetchLocations = async () => {
			try {
				const data = await makeRequest("get", "suapi/locations/");
				locations.value = data.results || data;
			} catch (err) {
				console.error("Error:", err);
			}
		};
		const fetchStats = async () => {
			try {
				stats.value = await makeRequest("get", "suapi/locations/stats/");
			} catch (err) {
				console.error("Error:", err);
			}
		};
		const refreshData = () => Promise.all([fetchLocations(), fetchStats()]);
		const openAddModal = () => {
			selectedLocation.value = null;
			formData.value = {
				name: "",
				code: "",
				location_type: "hotspot",
				city: "",
				max_concurrent_users: 100,
				router_ip: "",
				is_active: true,
				allow_roaming_in: true,
				address: ""
			};
			showFormModal.value = true;
		};
		const openEditModal = (location) => {
			selectedLocation.value = location;
			formData.value = {
				name: location.name || "",
				code: location.code || "",
				location_type: location.location_type || "hotspot",
				city: location.city || "",
				max_concurrent_users: location.max_concurrent_users || 100,
				router_ip: location.router_ip || "",
				is_active: location.is_active || false,
				allow_roaming_in: location.allow_roaming_in || false,
				address: location.address || ""
			};
			showFormModal.value = true;
		};
		const closeFormModal = () => {
			showFormModal.value = false;
			selectedLocation.value = null;
			formData.value = {
				name: "",
				code: "",
				location_type: "hotspot",
				city: "",
				max_concurrent_users: 100,
				router_ip: "",
				is_active: true,
				allow_roaming_in: true,
				address: ""
			};
		};
		const saveLocation = async () => {
			saveLoading.value = true;
			try {
				if (selectedLocation.value?.id) await makeRequest("patch", `suapi/locations/${selectedLocation.value.id}/`, formData.value);
				else await makeRequest("post", "suapi/locations/", formData.value);
				await refreshData();
				closeFormModal();
			} catch (err) {
				alert("Error: " + (err.response?.data?.error || JSON.stringify(err.response?.data) || err.message));
			} finally {
				saveLoading.value = false;
			}
		};
		const openDeleteModal = (location) => {
			locationToDelete.value = location;
			showDeleteModal.value = true;
		};
		const closeDeleteModal = () => {
			showDeleteModal.value = false;
			locationToDelete.value = null;
		};
		const confirmDelete = async () => {
			try {
				await makeRequest("delete", `suapi/locations/${locationToDelete.value.id}/`);
				await refreshData();
				closeDeleteModal();
			} catch (err) {
				alert("Error: " + (err.response?.data?.error || err.message));
			}
		};
		onMounted(refreshData);
		return {
			loading,
			error,
			locations,
			stats,
			searchTerm,
			statusFilter,
			showFormModal,
			showDeleteModal,
			selectedLocation,
			locationToDelete,
			saveLoading,
			formData,
			filteredLocations,
			fetchLocations,
			refreshData,
			openAddModal,
			openEditModal,
			closeFormModal,
			saveLocation,
			openDeleteModal,
			closeDeleteModal,
			confirmDelete
		};
	}
};
var _hoisted_1$9 = { class: "space-y-4 animate-fade-in" };
var _hoisted_2$9 = { class: "flex items-center justify-between" };
var _hoisted_3$9 = { class: "flex items-center gap-2" };
var _hoisted_4$9 = {
	key: 0,
	class: "bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-lg p-4"
};
var _hoisted_5$9 = { class: "flex items-center justify-between" };
var _hoisted_6$9 = { class: "flex items-center gap-3" };
var _hoisted_7$9 = { class: "text-xs text-rose-600 dark:text-rose-500 mt-1" };
var _hoisted_8$9 = { class: "grid grid-cols-2 md:grid-cols-4 gap-3 animate-slide-up" };
var _hoisted_9$8 = {
	class: "space-y-3 animate-slide-up",
	style: { "animation-delay": "0.1s" }
};
var _hoisted_10$8 = { class: "flex items-center gap-2" };
var _hoisted_11$7 = { class: "flex-1" };
var _hoisted_12$7 = { class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden" };
var _hoisted_13$7 = { class: "overflow-x-auto" };
var _hoisted_14$7 = { class: "w-full" };
var _hoisted_15$7 = { class: "divide-y divide-slate-200 dark:divide-slate-700" };
var _hoisted_16$7 = ["onClick"];
var _hoisted_17$7 = { class: "px-3 py-2" };
var _hoisted_18$7 = { class: "flex items-center gap-2" };
var _hoisted_19$6 = { class: "text-xs font-medium text-slate-900 dark:text-white" };
var _hoisted_20$6 = { class: "px-3 py-2 text-xs font-mono text-slate-900 dark:text-white" };
var _hoisted_21$6 = { class: "px-3 py-2" };
var _hoisted_22$6 = { class: "px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400" };
var _hoisted_23$6 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white" };
var _hoisted_24$6 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white" };
var _hoisted_25$6 = { class: "px-3 py-2" };
var _hoisted_26$6 = { class: "px-3 py-2 text-right" };
var _hoisted_27$6 = { class: "flex items-center justify-end gap-0.5" };
var _hoisted_28$6 = ["onClick"];
var _hoisted_29$6 = ["onClick"];
var _hoisted_30$6 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden" };
var _hoisted_31$6 = { class: "flex items-center justify-between p-5 border-b border-slate-200 dark:border-slate-700" };
var _hoisted_32$6 = { class: "text-base font-semibold text-slate-900 dark:text-white" };
var _hoisted_33$6 = { class: "p-5 overflow-y-auto max-h-[calc(90vh-140px)]" };
var _hoisted_34$6 = { class: "grid grid-cols-2 gap-4" };
var _hoisted_35$6 = { class: "flex items-center" };
var _hoisted_36$6 = { class: "flex items-center gap-2 cursor-pointer" };
var _hoisted_37$6 = { class: "flex items-center" };
var _hoisted_38$6 = { class: "flex items-center gap-2 cursor-pointer" };
var _hoisted_39$6 = { class: "col-span-2" };
var _hoisted_40$6 = { class: "flex items-center justify-end gap-2 p-5 border-t border-slate-200 dark:border-slate-700" };
var _hoisted_41$6 = ["disabled"];
function _sfc_render$9(_ctx, _cache, $props, $setup, $data, $options) {
	const _component_ModernMetricCard = resolveComponent("ModernMetricCard");
	const _component_ConfirmDialog = resolveComponent("ConfirmDialog");
	return openBlock(), createElementBlock("div", _hoisted_1$9, [
		createBaseVNode("div", _hoisted_2$9, [_cache[20] || (_cache[20] = createBaseVNode("div", null, [createBaseVNode("h1", { class: "text-lg font-semibold text-slate-900 dark:text-white" }, "Locations"), createBaseVNode("p", { class: "text-xs text-slate-500 dark:text-slate-400 mt-0.5" }, "Manage network locations")], -1)), createBaseVNode("div", _hoisted_3$9, [createBaseVNode("button", {
			onClick: _cache[0] || (_cache[0] = (...args) => $setup.openAddModal && $setup.openAddModal(...args)),
			class: "px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-xs flex items-center gap-1.5"
		}, [..._cache[18] || (_cache[18] = [createBaseVNode("svg", {
			class: "w-3.5 h-3.5",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M12 4v16m8-8H4"
		})], -1), createTextVNode(" Add Location ", -1)])]), createBaseVNode("button", {
			onClick: _cache[1] || (_cache[1] = (...args) => $setup.refreshData && $setup.refreshData(...args)),
			class: normalizeClass(["p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors", { "animate-spin": $setup.loading }])
		}, [..._cache[19] || (_cache[19] = [createBaseVNode("svg", {
			class: "w-4 h-4 text-slate-600 dark:text-slate-400",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
		})], -1)])], 2)])]),
		$setup.error ? (openBlock(), createElementBlock("div", _hoisted_4$9, [createBaseVNode("div", _hoisted_5$9, [createBaseVNode("div", _hoisted_6$9, [_cache[22] || (_cache[22] = createBaseVNode("svg", {
			class: "w-5 h-5 text-rose-600 dark:text-rose-400",
			fill: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" })], -1)), createBaseVNode("div", null, [_cache[21] || (_cache[21] = createBaseVNode("h3", { class: "text-sm font-medium text-rose-800 dark:text-rose-400" }, "Failed to load locations", -1)), createBaseVNode("p", _hoisted_7$9, toDisplayString($setup.error), 1)])]), createBaseVNode("button", {
			onClick: _cache[2] || (_cache[2] = (...args) => $setup.fetchLocations && $setup.fetchLocations(...args)),
			class: "px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm"
		}, "Retry")])])) : createCommentVNode("", true),
		createBaseVNode("div", _hoisted_8$9, [
			createVNode(_component_ModernMetricCard, {
				title: "Total",
				value: $setup.stats.total_locations,
				color: "blue"
			}, {
				default: withCtx(() => [..._cache[23] || (_cache[23] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Active",
				value: $setup.stats.active_locations,
				color: "emerald"
			}, {
				default: withCtx(() => [..._cache[24] || (_cache[24] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Hotspots",
				value: $setup.stats.hotspot_locations,
				color: "purple"
			}, {
				default: withCtx(() => [..._cache[25] || (_cache[25] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Branches",
				value: $setup.stats.branch_locations,
				color: "amber"
			}, {
				default: withCtx(() => [..._cache[26] || (_cache[26] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" })], -1)])]),
				_: 1
			}, 8, ["value"])
		]),
		createBaseVNode("div", _hoisted_9$8, [createBaseVNode("div", _hoisted_10$8, [createBaseVNode("div", _hoisted_11$7, [withDirectives(createBaseVNode("input", {
			"onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => $setup.searchTerm = $event),
			type: "text",
			placeholder: "Search locations...",
			class: "w-full px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs"
		}, null, 512), [[vModelText, $setup.searchTerm]])]), withDirectives(createBaseVNode("select", {
			"onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => $setup.statusFilter = $event),
			class: "px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs"
		}, [..._cache[27] || (_cache[27] = [
			createBaseVNode("option", { value: "" }, "All Status", -1),
			createBaseVNode("option", { value: "true" }, "Active", -1),
			createBaseVNode("option", { value: "false" }, "Inactive", -1)
		])], 512), [[vModelSelect, $setup.statusFilter]])]), createBaseVNode("div", _hoisted_12$7, [createBaseVNode("div", _hoisted_13$7, [createBaseVNode("table", _hoisted_14$7, [_cache[31] || (_cache[31] = createBaseVNode("thead", { class: "bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700" }, [createBaseVNode("tr", null, [
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Location"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Code"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Type"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "City"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Capacity"),
			createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Status"),
			createBaseVNode("th", { class: "px-3 py-2 text-right text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Actions")
		])], -1)), createBaseVNode("tbody", _hoisted_15$7, [(openBlock(true), createElementBlock(Fragment, null, renderList($setup.filteredLocations, (location) => {
			return openBlock(), createElementBlock("tr", {
				key: location.id,
				onClick: ($event) => $setup.openEditModal(location),
				class: "hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer"
			}, [
				createBaseVNode("td", _hoisted_17$7, [createBaseVNode("div", _hoisted_18$7, [_cache[28] || (_cache[28] = createBaseVNode("div", { class: "w-7 h-7 rounded-lg bg-gradient-to-br from-green-500 to-teal-600 flex items-center justify-center" }, [createBaseVNode("svg", {
					class: "w-4 h-4 text-white",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" })])], -1)), createBaseVNode("p", _hoisted_19$6, toDisplayString(location.name), 1)])]),
				createBaseVNode("td", _hoisted_20$6, toDisplayString(location.code), 1),
				createBaseVNode("td", _hoisted_21$6, [createBaseVNode("span", _hoisted_22$6, toDisplayString(location.location_type), 1)]),
				createBaseVNode("td", _hoisted_23$6, toDisplayString(location.city || "N/A"), 1),
				createBaseVNode("td", _hoisted_24$6, toDisplayString(location.max_concurrent_users), 1),
				createBaseVNode("td", _hoisted_25$6, [createBaseVNode("span", { class: normalizeClass(["px-1.5 py-0.5 text-[10px] font-medium rounded-full", location.is_active ? "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400" : "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400"]) }, toDisplayString(location.is_active ? "Active" : "Inactive"), 3)]),
				createBaseVNode("td", _hoisted_26$6, [createBaseVNode("div", _hoisted_27$6, [createBaseVNode("button", {
					onClick: withModifiers(($event) => $setup.openEditModal(location), ["stop"]),
					class: "p-1 hover:bg-blue-100 dark:hover:bg-blue-600 rounded transition-colors",
					title: "Edit"
				}, [..._cache[29] || (_cache[29] = [createBaseVNode("svg", {
					class: "w-3.5 h-3.5 text-blue-600 dark:text-blue-400",
					fill: "none",
					stroke: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", {
					"stroke-linecap": "round",
					"stroke-linejoin": "round",
					"stroke-width": "2",
					d: "M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
				})], -1)])], 8, _hoisted_28$6), createBaseVNode("button", {
					onClick: withModifiers(($event) => $setup.openDeleteModal(location), ["stop"]),
					class: "p-1 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors",
					title: "Delete"
				}, [..._cache[30] || (_cache[30] = [createBaseVNode("svg", {
					class: "w-3.5 h-3.5 text-red-600 dark:text-red-400",
					fill: "none",
					stroke: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", {
					"stroke-linecap": "round",
					"stroke-linejoin": "round",
					"stroke-width": "2",
					d: "M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
				})], -1)])], 8, _hoisted_29$6)])])
			], 8, _hoisted_16$7);
		}), 128))])])])])]),
		$setup.showFormModal ? (openBlock(), createElementBlock("div", {
			key: 1,
			class: "fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4",
			onClick: _cache[17] || (_cache[17] = withModifiers((...args) => $setup.closeFormModal && $setup.closeFormModal(...args), ["self"]))
		}, [createBaseVNode("div", _hoisted_30$6, [
			createBaseVNode("div", _hoisted_31$6, [createBaseVNode("h2", _hoisted_32$6, toDisplayString($setup.selectedLocation?.id ? "Edit Location" : "Add Location"), 1), createBaseVNode("button", {
				onClick: _cache[5] || (_cache[5] = (...args) => $setup.closeFormModal && $setup.closeFormModal(...args)),
				class: "p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
			}, [..._cache[32] || (_cache[32] = [createBaseVNode("svg", {
				class: "w-4 h-4",
				fill: "none",
				stroke: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M6 18L18 6M6 6l12 12"
			})], -1)])])]),
			createBaseVNode("div", _hoisted_33$6, [createBaseVNode("div", _hoisted_34$6, [
				createBaseVNode("div", null, [_cache[33] || (_cache[33] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Name *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => $setup.formData.name = $event),
					type: "text",
					required: "",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.name]])]),
				createBaseVNode("div", null, [_cache[34] || (_cache[34] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Code *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => $setup.formData.code = $event),
					type: "text",
					required: "",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.code]])]),
				createBaseVNode("div", null, [_cache[36] || (_cache[36] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Type *", -1)), withDirectives(createBaseVNode("select", {
					"onUpdate:modelValue": _cache[8] || (_cache[8] = ($event) => $setup.formData.location_type = $event),
					required: "",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, [..._cache[35] || (_cache[35] = [createStaticVNode("<option value=\"headquarters\" data-v-44e51608>Headquarters</option><option value=\"branch\" data-v-44e51608>Branch</option><option value=\"hotspot\" data-v-44e51608>Hotspot</option><option value=\"commercial\" data-v-44e51608>Commercial</option><option value=\"fallback\" data-v-44e51608>Fallback</option>", 5)])], 512), [[vModelSelect, $setup.formData.location_type]])]),
				createBaseVNode("div", null, [_cache[37] || (_cache[37] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "City", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[9] || (_cache[9] = ($event) => $setup.formData.city = $event),
					type: "text",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.city]])]),
				createBaseVNode("div", null, [_cache[38] || (_cache[38] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Max Users", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[10] || (_cache[10] = ($event) => $setup.formData.max_concurrent_users = $event),
					type: "number",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.max_concurrent_users]])]),
				createBaseVNode("div", null, [_cache[39] || (_cache[39] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Router IP", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[11] || (_cache[11] = ($event) => $setup.formData.router_ip = $event),
					type: "text",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.router_ip]])]),
				createBaseVNode("div", _hoisted_35$6, [createBaseVNode("label", _hoisted_36$6, [withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[12] || (_cache[12] = ($event) => $setup.formData.is_active = $event),
					type: "checkbox",
					class: "w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded"
				}, null, 512), [[vModelCheckbox, $setup.formData.is_active]]), _cache[40] || (_cache[40] = createBaseVNode("span", { class: "text-xs text-slate-700 dark:text-slate-300" }, "Active", -1))])]),
				createBaseVNode("div", _hoisted_37$6, [createBaseVNode("label", _hoisted_38$6, [withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[13] || (_cache[13] = ($event) => $setup.formData.allow_roaming_in = $event),
					type: "checkbox",
					class: "w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded"
				}, null, 512), [[vModelCheckbox, $setup.formData.allow_roaming_in]]), _cache[41] || (_cache[41] = createBaseVNode("span", { class: "text-xs text-slate-700 dark:text-slate-300" }, "Allow Roaming In", -1))])]),
				createBaseVNode("div", _hoisted_39$6, [_cache[42] || (_cache[42] = createBaseVNode("label", { class: "block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1" }, "Address", -1)), withDirectives(createBaseVNode("textarea", {
					"onUpdate:modelValue": _cache[14] || (_cache[14] = ($event) => $setup.formData.address = $event),
					rows: "2",
					class: "w-full px-3 py-2 text-xs bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $setup.formData.address]])])
			])]),
			createBaseVNode("div", _hoisted_40$6, [createBaseVNode("button", {
				onClick: _cache[15] || (_cache[15] = (...args) => $setup.closeFormModal && $setup.closeFormModal(...args)),
				class: "px-3 py-2 text-xs bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg"
			}, "Cancel"), createBaseVNode("button", {
				onClick: _cache[16] || (_cache[16] = (...args) => $setup.saveLocation && $setup.saveLocation(...args)),
				disabled: $setup.saveLoading,
				class: normalizeClass(["px-3 py-2 text-xs bg-blue-500 hover:bg-blue-600 text-white rounded-lg", { "opacity-50": $setup.saveLoading }])
			}, toDisplayString($setup.saveLoading ? "Saving..." : $setup.selectedLocation?.id ? "Update" : "Create"), 11, _hoisted_41$6)])
		])])) : createCommentVNode("", true),
		createVNode(_component_ConfirmDialog, {
			show: $setup.showDeleteModal,
			title: "Delete Location",
			message: `Delete location ${$setup.locationToDelete?.name}?`,
			type: "danger",
			onConfirm: $setup.confirmDelete,
			onCancel: $setup.closeDeleteModal
		}, null, 8, [
			"show",
			"message",
			"onConfirm",
			"onCancel"
		])
	]);
}
var Locations_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$9, [["render", _sfc_render$9], ["__scopeId", "data-v-44e51608"]]);
var _sfc_main$8 = {
	name: "Transactions",
	components: { ModernMetricCard: MetricCard_default },
	setup() {
		const { loading, error, makeRequest } = useApi();
		const activeTab = ref("payments");
		const searchTerm = ref("");
		const statusFilter = ref("");
		const stats = ref({});
		const payments = ref([]);
		const balance = ref([]);
		const queue = ref([]);
		const points = ref([]);
		const tabs = [
			{
				id: "payments",
				label: "Payment Transactions"
			},
			{
				id: "balance",
				label: "Balance Transactions"
			},
			{
				id: "queue",
				label: "Transaction Queue"
			},
			{
				id: "points",
				label: "Point Transactions"
			}
		];
		const filteredPayments = computed(() => {
			let result = payments.value;
			if (searchTerm.value) {
				const term = searchTerm.value.toLowerCase();
				result = result.filter((t) => t.transaction_id?.toLowerCase().includes(term) || t.initiator?.toLowerCase().includes(term));
			}
			return result;
		});
		const filteredBalance = computed(() => {
			let result = balance.value;
			if (searchTerm.value) {
				const term = searchTerm.value.toLowerCase();
				result = result.filter((t) => t.user_account?.toLowerCase().includes(term) || t.description?.toLowerCase().includes(term));
			}
			return result;
		});
		const filteredQueue = computed(() => {
			let result = queue.value;
			if (searchTerm.value) {
				const term = searchTerm.value.toLowerCase();
				result = result.filter((t) => t.initiator?.toLowerCase().includes(term) || t.package?.toLowerCase().includes(term));
			}
			if (statusFilter.value) result = result.filter((t) => t.status === statusFilter.value);
			return result;
		});
		const filteredPoints = computed(() => {
			let result = points.value;
			if (searchTerm.value) {
				const term = searchTerm.value.toLowerCase();
				result = result.filter((t) => t.user_account?.toLowerCase().includes(term) || t.description?.toLowerCase().includes(term));
			}
			return result;
		});
		const fetchPayments = async () => {
			try {
				const data = await makeRequest("get", "suapi/payment-transactions/");
				payments.value = data.results || data;
			} catch (err) {
				console.error("Error:", err);
			}
		};
		const fetchBalance = async () => {
			try {
				const data = await makeRequest("get", "suapi/balance-transactions/");
				balance.value = data.results || data;
			} catch (err) {
				console.error("Error:", err);
			}
		};
		const fetchQueue = async () => {
			try {
				const data = await makeRequest("get", "suapi/transaction-queue/");
				queue.value = data.results || data;
			} catch (err) {
				console.error("Error:", err);
			}
		};
		const fetchPoints = async () => {
			try {
				const data = await makeRequest("get", "suapi/point-transactions-txn/");
				points.value = data.results || data;
			} catch (err) {
				console.error("Error:", err);
			}
		};
		const fetchStats = async () => {
			try {
				const data = await makeRequest("get", "finance/api/transaction-stats/");
				stats.value = {
					total_revenue: data.queue.total_amount || 0,
					completed_count: data.queue.completed || 0,
					pending_count: data.queue.pending || 0,
					failed_count: data.queue.failed || 0
				};
			} catch (err) {
				console.error("Error fetching stats:", err);
				stats.value = {
					total_revenue: 0,
					completed_count: 0,
					pending_count: 0,
					failed_count: 0
				};
			}
		};
		const refreshData = async () => {
			await fetchStats();
			await Promise.all([
				fetchPayments(),
				fetchBalance(),
				fetchQueue(),
				fetchPoints()
			]);
		};
		const formatCurrency = (amount) => {
			if (!amount) return "KSh 0";
			return `KSh ${parseFloat(amount).toLocaleString()}`;
		};
		const formatDate = (date) => {
			if (!date) return "N/A";
			return new Date(date).toLocaleString("en-US", {
				month: "short",
				day: "numeric",
				year: "numeric",
				hour: "2-digit",
				minute: "2-digit"
			});
		};
		const getStatusClass = (status) => {
			return {
				completed: "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400",
				refunded: "bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400",
				partially_refunded: "bg-orange-100 dark:bg-orange-500/20 text-orange-700 dark:text-orange-400"
			}[status] || "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400";
		};
		const getQueueStatusClass = (status) => {
			return {
				pending: "bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400",
				processing: "bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400",
				completed: "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400",
				failed: "bg-rose-100 dark:bg-rose-500/20 text-rose-700 dark:text-rose-400",
				processed: "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400"
			}[status] || "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-400";
		};
		onMounted(refreshData);
		return {
			loading,
			error,
			activeTab,
			searchTerm,
			statusFilter,
			stats,
			tabs,
			filteredPayments,
			filteredBalance,
			filteredQueue,
			filteredPoints,
			refreshData,
			formatCurrency,
			formatDate,
			getStatusClass,
			getQueueStatusClass
		};
	}
};
var _hoisted_1$8 = { class: "space-y-4 animate-fade-in" };
var _hoisted_2$8 = { class: "flex items-center justify-between" };
var _hoisted_3$8 = {
	key: 0,
	class: "bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-lg p-4"
};
var _hoisted_4$8 = { class: "flex items-center justify-between" };
var _hoisted_5$8 = { class: "flex items-center gap-3" };
var _hoisted_6$8 = { class: "text-xs text-rose-600 dark:text-rose-500 mt-1" };
var _hoisted_7$8 = { class: "grid grid-cols-2 md:grid-cols-4 gap-3 animate-slide-up" };
var _hoisted_8$8 = {
	class: "bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden animate-slide-up",
	style: { "animation-delay": "0.1s" }
};
var _hoisted_9$7 = { class: "border-b border-slate-200 dark:border-slate-700" };
var _hoisted_10$7 = { class: "flex overflow-x-auto" };
var _hoisted_11$6 = ["onClick"];
var _hoisted_12$6 = { class: "p-4 space-y-3" };
var _hoisted_13$6 = { class: "flex items-center gap-2" };
var _hoisted_14$6 = {
	key: 0,
	class: "overflow-x-auto"
};
var _hoisted_15$6 = { class: "w-full" };
var _hoisted_16$6 = { class: "divide-y divide-slate-200 dark:divide-slate-700" };
var _hoisted_17$6 = { class: "px-3 py-2 text-xs font-mono text-slate-900 dark:text-white" };
var _hoisted_18$6 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white" };
var _hoisted_19$5 = { class: "px-3 py-2 text-xs font-semibold text-emerald-600 dark:text-emerald-400" };
var _hoisted_20$5 = { class: "px-3 py-2" };
var _hoisted_21$5 = { class: "px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400" };
var _hoisted_22$5 = { class: "px-3 py-2" };
var _hoisted_23$5 = { class: "px-3 py-2 text-xs text-slate-600 dark:text-slate-400" };
var _hoisted_24$5 = {
	key: 1,
	class: "overflow-x-auto"
};
var _hoisted_25$5 = { class: "w-full" };
var _hoisted_26$5 = { class: "divide-y divide-slate-200 dark:divide-slate-700" };
var _hoisted_27$5 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white" };
var _hoisted_28$5 = { class: "px-3 py-2" };
var _hoisted_29$5 = { class: "px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400" };
var _hoisted_30$5 = { class: "px-3 py-2 text-xs text-slate-600 dark:text-slate-400" };
var _hoisted_31$5 = { class: "px-3 py-2 text-xs text-slate-600 dark:text-slate-400" };
var _hoisted_32$5 = { class: "px-3 py-2 text-xs text-slate-600 dark:text-slate-400" };
var _hoisted_33$5 = { class: "px-3 py-2 text-xs text-slate-600 dark:text-slate-400" };
var _hoisted_34$5 = {
	key: 2,
	class: "overflow-x-auto"
};
var _hoisted_35$5 = { class: "w-full" };
var _hoisted_36$5 = { class: "divide-y divide-slate-200 dark:divide-slate-700" };
var _hoisted_37$5 = { class: "px-3 py-2" };
var _hoisted_38$5 = { class: "px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-indigo-100 dark:bg-indigo-500/20 text-indigo-700 dark:text-indigo-400" };
var _hoisted_39$5 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white" };
var _hoisted_40$5 = { class: "px-3 py-2 text-xs text-slate-600 dark:text-slate-400" };
var _hoisted_41$5 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white" };
var _hoisted_42$5 = { class: "px-3 py-2 text-xs text-slate-600 dark:text-slate-400" };
var _hoisted_43$5 = { class: "px-3 py-2" };
var _hoisted_44$5 = { class: "px-3 py-2 text-xs text-slate-600 dark:text-slate-400" };
var _hoisted_45$4 = { class: "px-3 py-2 text-xs text-slate-600 dark:text-slate-400" };
var _hoisted_46$4 = {
	key: 3,
	class: "overflow-x-auto"
};
var _hoisted_47$4 = { class: "w-full" };
var _hoisted_48$3 = { class: "divide-y divide-slate-200 dark:divide-slate-700" };
var _hoisted_49$3 = { class: "px-3 py-2 text-xs text-slate-900 dark:text-white" };
var _hoisted_50$3 = { class: "px-3 py-2" };
var _hoisted_51$3 = { class: "px-1.5 py-0.5 text-[10px] font-medium rounded-full bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400" };
var _hoisted_52$2 = { class: "px-3 py-2 text-xs text-slate-600 dark:text-slate-400" };
var _hoisted_53$2 = { class: "px-3 py-2 text-xs text-slate-600 dark:text-slate-400" };
function _sfc_render$8(_ctx, _cache, $props, $setup, $data, $options) {
	const _component_ModernMetricCard = resolveComponent("ModernMetricCard");
	return openBlock(), createElementBlock("div", _hoisted_1$8, [
		createBaseVNode("div", _hoisted_2$8, [_cache[5] || (_cache[5] = createBaseVNode("div", null, [createBaseVNode("h1", { class: "text-lg font-semibold text-slate-900 dark:text-white" }, "Transactions"), createBaseVNode("p", { class: "text-xs text-slate-500 dark:text-slate-400 mt-0.5" }, "All transaction types")], -1)), createBaseVNode("button", {
			onClick: _cache[0] || (_cache[0] = (...args) => $setup.refreshData && $setup.refreshData(...args)),
			class: normalizeClass(["p-1.5 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors", { "animate-spin": $setup.loading }])
		}, [..._cache[4] || (_cache[4] = [createBaseVNode("svg", {
			class: "w-4 h-4 text-slate-600 dark:text-slate-400",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
		})], -1)])], 2)]),
		$setup.error ? (openBlock(), createElementBlock("div", _hoisted_3$8, [createBaseVNode("div", _hoisted_4$8, [createBaseVNode("div", _hoisted_5$8, [_cache[7] || (_cache[7] = createBaseVNode("svg", {
			class: "w-5 h-5 text-rose-600 dark:text-rose-400",
			fill: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" })], -1)), createBaseVNode("div", null, [_cache[6] || (_cache[6] = createBaseVNode("h3", { class: "text-sm font-medium text-rose-800 dark:text-rose-400" }, "Failed to load transactions", -1)), createBaseVNode("p", _hoisted_6$8, toDisplayString($setup.error), 1)])]), createBaseVNode("button", {
			onClick: _cache[1] || (_cache[1] = (...args) => $setup.refreshData && $setup.refreshData(...args)),
			class: "px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm"
		}, "Retry")])])) : createCommentVNode("", true),
		createBaseVNode("div", _hoisted_7$8, [
			createVNode(_component_ModernMetricCard, {
				title: "Total Revenue",
				value: $setup.formatCurrency($setup.stats.total_revenue),
				color: "emerald"
			}, {
				default: withCtx(() => [..._cache[8] || (_cache[8] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1.41 16.09V20h-2.67v-1.93c-1.71-.36-3.16-1.46-3.27-3.4h1.96c.1 1.05.82 1.87 2.65 1.87 1.96 0 2.4-.98 2.4-1.59 0-.83-.44-1.61-2.67-2.14-2.48-.6-4.18-1.62-4.18-3.67 0-1.72 1.39-2.84 3.11-3.21V4h2.67v1.95c1.86.45 2.79 1.86 2.85 3.39H14.3c-.05-1.11-.64-1.87-2.22-1.87-1.5 0-2.4.68-2.4 1.64 0 .84.65 1.39 2.67 1.91s4.18 1.39 4.18 3.91c-.01 1.83-1.38 2.83-3.12 3.16z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Completed",
				value: $setup.stats.completed_count,
				color: "blue"
			}, {
				default: withCtx(() => [..._cache[9] || (_cache[9] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Pending",
				value: $setup.stats.pending_count,
				color: "amber"
			}, {
				default: withCtx(() => [..._cache[10] || (_cache[10] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm4.2 14.2L11 13V7h1.5v5.2l4.5 2.7-.8 1.3z" })], -1)])]),
				_: 1
			}, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Failed",
				value: $setup.stats.failed_count,
				color: "rose"
			}, {
				default: withCtx(() => [..._cache[11] || (_cache[11] = [createBaseVNode("svg", {
					class: "w-6 h-6",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" })], -1)])]),
				_: 1
			}, 8, ["value"])
		]),
		createBaseVNode("div", _hoisted_8$8, [createBaseVNode("div", _hoisted_9$7, [createBaseVNode("div", _hoisted_10$7, [(openBlock(true), createElementBlock(Fragment, null, renderList($setup.tabs, (tab) => {
			return openBlock(), createElementBlock("button", {
				key: tab.id,
				onClick: ($event) => $setup.activeTab = tab.id,
				class: normalizeClass(["px-4 py-2.5 text-xs font-medium whitespace-nowrap transition-colors", $setup.activeTab === tab.id ? "text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400" : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"])
			}, toDisplayString(tab.label), 11, _hoisted_11$6);
		}), 128))])]), createBaseVNode("div", _hoisted_12$6, [
			createBaseVNode("div", _hoisted_13$6, [withDirectives(createBaseVNode("input", {
				"onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => $setup.searchTerm = $event),
				type: "text",
				placeholder: "Search transactions...",
				class: "flex-1 px-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs"
			}, null, 512), [[vModelText, $setup.searchTerm]]), $setup.activeTab === "queue" ? withDirectives((openBlock(), createElementBlock("select", {
				key: 0,
				"onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => $setup.statusFilter = $event),
				class: "px-3 py-1.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white text-xs"
			}, [..._cache[12] || (_cache[12] = [createStaticVNode("<option value=\"\" data-v-935ffbe0>All Status</option><option value=\"pending\" data-v-935ffbe0>Pending</option><option value=\"processing\" data-v-935ffbe0>Processing</option><option value=\"completed\" data-v-935ffbe0>Completed</option><option value=\"failed\" data-v-935ffbe0>Failed</option>", 5)])], 512)), [[vModelSelect, $setup.statusFilter]]) : createCommentVNode("", true)]),
			$setup.activeTab === "payments" ? (openBlock(), createElementBlock("div", _hoisted_14$6, [createBaseVNode("table", _hoisted_15$6, [_cache[13] || (_cache[13] = createBaseVNode("thead", { class: "bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700" }, [createBaseVNode("tr", null, [
				createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Transaction ID"),
				createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "User"),
				createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Amount"),
				createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Method"),
				createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Status"),
				createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Date")
			])], -1)), createBaseVNode("tbody", _hoisted_16$6, [(openBlock(true), createElementBlock(Fragment, null, renderList($setup.filteredPayments, (txn) => {
				return openBlock(), createElementBlock("tr", {
					key: txn.id,
					class: "hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors"
				}, [
					createBaseVNode("td", _hoisted_17$6, toDisplayString(txn.transaction_id?.substring(0, 12)) + "...", 1),
					createBaseVNode("td", _hoisted_18$6, toDisplayString(txn.initiator), 1),
					createBaseVNode("td", _hoisted_19$5, toDisplayString($setup.formatCurrency(txn.amount)), 1),
					createBaseVNode("td", _hoisted_20$5, [createBaseVNode("span", _hoisted_21$5, toDisplayString(txn.payment_method), 1)]),
					createBaseVNode("td", _hoisted_22$5, [createBaseVNode("span", { class: normalizeClass(["px-1.5 py-0.5 text-[10px] font-medium rounded-full", $setup.getStatusClass(txn.status)]) }, toDisplayString(txn.status), 3)]),
					createBaseVNode("td", _hoisted_23$5, toDisplayString($setup.formatDate(txn.created_at)), 1)
				]);
			}), 128))])])])) : createCommentVNode("", true),
			$setup.activeTab === "balance" ? (openBlock(), createElementBlock("div", _hoisted_24$5, [createBaseVNode("table", _hoisted_25$5, [_cache[14] || (_cache[14] = createBaseVNode("thead", { class: "bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700" }, [createBaseVNode("tr", null, [
				createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "User"),
				createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Type"),
				createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Amount"),
				createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Balance Before"),
				createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Balance After"),
				createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Description"),
				createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Date")
			])], -1)), createBaseVNode("tbody", _hoisted_26$5, [(openBlock(true), createElementBlock(Fragment, null, renderList($setup.filteredBalance, (txn) => {
				return openBlock(), createElementBlock("tr", {
					key: txn.id,
					class: "hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors"
				}, [
					createBaseVNode("td", _hoisted_27$5, toDisplayString(txn.user_account || txn.user), 1),
					createBaseVNode("td", _hoisted_28$5, [createBaseVNode("span", _hoisted_29$5, toDisplayString(txn.transaction_type), 1)]),
					createBaseVNode("td", { class: normalizeClass(["px-3 py-2 text-xs font-semibold", txn.credit > 0 ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400"]) }, toDisplayString(txn.credit > 0 ? "+" : "-") + toDisplayString($setup.formatCurrency(Math.abs(txn.credit || txn.debit))), 3),
					createBaseVNode("td", _hoisted_30$5, toDisplayString($setup.formatCurrency(txn.balance_before)), 1),
					createBaseVNode("td", _hoisted_31$5, toDisplayString($setup.formatCurrency(txn.balance_after)), 1),
					createBaseVNode("td", _hoisted_32$5, toDisplayString(txn.description), 1),
					createBaseVNode("td", _hoisted_33$5, toDisplayString($setup.formatDate(txn.created_at)), 1)
				]);
			}), 128))])])])) : createCommentVNode("", true),
			$setup.activeTab === "queue" ? (openBlock(), createElementBlock("div", _hoisted_34$5, [createBaseVNode("table", _hoisted_35$5, [_cache[15] || (_cache[15] = createBaseVNode("thead", { class: "bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700" }, [createBaseVNode("tr", null, [
				createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Type"),
				createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "User"),
				createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Package"),
				createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Price"),
				createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Method"),
				createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Status"),
				createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Retries"),
				createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Date")
			])], -1)), createBaseVNode("tbody", _hoisted_36$5, [(openBlock(true), createElementBlock(Fragment, null, renderList($setup.filteredQueue, (txn) => {
				return openBlock(), createElementBlock("tr", {
					key: txn.id,
					class: "hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors"
				}, [
					createBaseVNode("td", _hoisted_37$5, [createBaseVNode("span", _hoisted_38$5, toDisplayString(txn.queue_type), 1)]),
					createBaseVNode("td", _hoisted_39$5, toDisplayString(txn.initiator), 1),
					createBaseVNode("td", _hoisted_40$5, toDisplayString(txn.package), 1),
					createBaseVNode("td", _hoisted_41$5, toDisplayString($setup.formatCurrency(txn.price)), 1),
					createBaseVNode("td", _hoisted_42$5, toDisplayString(txn.method), 1),
					createBaseVNode("td", _hoisted_43$5, [createBaseVNode("span", { class: normalizeClass(["px-1.5 py-0.5 text-[10px] font-medium rounded-full", $setup.getQueueStatusClass(txn.status)]) }, toDisplayString(txn.status), 3)]),
					createBaseVNode("td", _hoisted_44$5, toDisplayString(txn.retry_count) + "/" + toDisplayString(txn.max_retries), 1),
					createBaseVNode("td", _hoisted_45$4, toDisplayString($setup.formatDate(txn.created_at)), 1)
				]);
			}), 128))])])])) : createCommentVNode("", true),
			$setup.activeTab === "points" ? (openBlock(), createElementBlock("div", _hoisted_46$4, [createBaseVNode("table", _hoisted_47$4, [_cache[16] || (_cache[16] = createBaseVNode("thead", { class: "bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700" }, [createBaseVNode("tr", null, [
				createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "User"),
				createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Type"),
				createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Points"),
				createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Description"),
				createBaseVNode("th", { class: "px-3 py-2 text-left text-[10px] font-medium text-slate-600 dark:text-slate-400" }, "Date")
			])], -1)), createBaseVNode("tbody", _hoisted_48$3, [(openBlock(true), createElementBlock(Fragment, null, renderList($setup.filteredPoints, (txn) => {
				return openBlock(), createElementBlock("tr", {
					key: txn.id,
					class: "hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors"
				}, [
					createBaseVNode("td", _hoisted_49$3, toDisplayString(txn.user_account || txn.user), 1),
					createBaseVNode("td", _hoisted_50$3, [createBaseVNode("span", _hoisted_51$3, toDisplayString(txn.transaction_type), 1)]),
					createBaseVNode("td", { class: normalizeClass(["px-3 py-2 text-xs font-semibold", txn.points > 0 ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400"]) }, toDisplayString(txn.points > 0 ? "+" : "") + toDisplayString(txn.points), 3),
					createBaseVNode("td", _hoisted_52$2, toDisplayString(txn.description), 1),
					createBaseVNode("td", _hoisted_53$2, toDisplayString($setup.formatDate(txn.created_at)), 1)
				]);
			}), 128))])])])) : createCommentVNode("", true)
		])])
	]);
}
var Transactions_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$8, [["render", _sfc_render$8], ["__scopeId", "data-v-935ffbe0"]]);
var _sfc_main$7 = {
	name: "Refunds",
	components: {
		ModernMetricCard: MetricCard_default,
		SearchBar: SearchBar_default,
		DataTable: DataTable_default,
		ArrowPathIcon: render$9,
		ExclamationTriangleIcon: render$7
	},
	setup() {
		const { loading, error, makeRequest } = useApi();
		const refunds = ref([]);
		const stats = ref({});
		const searchTerm = ref("");
		const activeFilters = ref({});
		const columns = [
			{
				key: "id",
				label: "ID",
				sortable: true
			},
			{
				key: "client_username",
				label: "Client",
				sortable: true
			},
			{
				key: "amount",
				label: "Amount",
				sortable: true,
				format: (v) => `KSh ${v}`
			},
			{
				key: "downtime_minutes",
				label: "Downtime (min)",
				sortable: true
			},
			{
				key: "status",
				label: "Status",
				sortable: true
			},
			{
				key: "created_at",
				label: "Date",
				sortable: true,
				format: (v) => new Date(v).toLocaleDateString()
			}
		];
		const filters = [{
			key: "status",
			label: "Status",
			options: [{
				value: "completed",
				label: "Completed"
			}, {
				value: "pending",
				label: "Pending"
			}]
		}];
		const filteredRefunds = computed(() => {
			let result = refunds.value;
			if (searchTerm.value) {
				const term = searchTerm.value.toLowerCase();
				result = result.filter((r) => r.client_username?.toLowerCase().includes(term));
			}
			Object.keys(activeFilters.value).forEach((key) => {
				const value = activeFilters.value[key];
				if (value) result = result.filter((r) => r[key] === value);
			});
			return result;
		});
		const fetchRefunds = async () => {
			try {
				const data = await makeRequest("get", "suapi/refunds/history/");
				refunds.value = data.results || data;
			} catch (err) {
				console.error("Error:", err);
			}
		};
		const fetchStats = async () => {
			try {
				stats.value = await makeRequest("get", "suapi/refunds/stats/");
			} catch (err) {
				console.error("Error:", err);
			}
		};
		const refreshData = () => Promise.all([fetchRefunds(), fetchStats()]);
		const handleFilterChange = ({ all }) => {
			activeFilters.value = all;
		};
		const clearFilters = () => {
			searchTerm.value = "";
			activeFilters.value = {};
		};
		const formatNumber = (num) => new Intl.NumberFormat().format(num);
		onMounted(refreshData);
		return {
			loading,
			error,
			refunds,
			stats,
			searchTerm,
			columns,
			filters,
			filteredRefunds,
			fetchRefunds,
			refreshData,
			handleFilterChange,
			clearFilters,
			formatNumber
		};
	}
};
var _hoisted_1$7 = { class: "space-y-6 animate-fade-in" };
var _hoisted_2$7 = { class: "flex items-center justify-between" };
var _hoisted_3$7 = {
	key: 0,
	class: "bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/20 rounded-lg p-4"
};
var _hoisted_4$7 = { class: "flex items-center justify-between" };
var _hoisted_5$7 = { class: "flex items-center gap-3" };
var _hoisted_6$7 = { class: "text-xs text-rose-600 dark:text-rose-500 mt-1" };
var _hoisted_7$7 = { class: "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-slide-up" };
var _hoisted_8$7 = {
	class: "space-y-4 animate-slide-up",
	style: { "animation-delay": "0.1s" }
};
function _sfc_render$7(_ctx, _cache, $props, $setup, $data, $options) {
	const _component_ArrowPathIcon = resolveComponent("ArrowPathIcon");
	const _component_ExclamationTriangleIcon = resolveComponent("ExclamationTriangleIcon");
	const _component_ModernMetricCard = resolveComponent("ModernMetricCard");
	const _component_SearchBar = resolveComponent("SearchBar");
	const _component_DataTable = resolveComponent("DataTable");
	return openBlock(), createElementBlock("div", _hoisted_1$7, [
		createBaseVNode("div", _hoisted_2$7, [_cache[3] || (_cache[3] = createBaseVNode("div", null, [createBaseVNode("h1", { class: "text-2xl font-semibold text-slate-900 dark:text-white" }, "Refunds"), createBaseVNode("p", { class: "text-sm text-slate-500 dark:text-slate-400 mt-1" }, "Manage downtime refunds")], -1)), createBaseVNode("button", {
			onClick: _cache[0] || (_cache[0] = (...args) => $setup.refreshData && $setup.refreshData(...args)),
			class: normalizeClass(["p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors", { "animate-spin": $setup.loading }])
		}, [createVNode(_component_ArrowPathIcon, { class: "w-5 h-5 text-slate-600 dark:text-slate-400" })], 2)]),
		$setup.error ? (openBlock(), createElementBlock("div", _hoisted_3$7, [createBaseVNode("div", _hoisted_4$7, [createBaseVNode("div", _hoisted_5$7, [createVNode(_component_ExclamationTriangleIcon, { class: "w-5 h-5 text-rose-600 dark:text-rose-400" }), createBaseVNode("div", null, [_cache[4] || (_cache[4] = createBaseVNode("h3", { class: "text-sm font-medium text-rose-800 dark:text-rose-400" }, "Failed to load refunds", -1)), createBaseVNode("p", _hoisted_6$7, toDisplayString($setup.error), 1)])]), createBaseVNode("button", {
			onClick: _cache[1] || (_cache[1] = (...args) => $setup.fetchRefunds && $setup.fetchRefunds(...args)),
			class: "px-3 py-1.5 bg-rose-600 text-white rounded-lg hover:bg-rose-700 text-sm"
		}, "Retry")])])) : createCommentVNode("", true),
		createBaseVNode("div", _hoisted_7$7, [
			createVNode(_component_ModernMetricCard, {
				title: "Eligible Clients",
				value: $setup.stats.eligible_clients,
				icon: "👥",
				color: "blue"
			}, null, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Total Refunded",
				value: `KSh ${$setup.formatNumber($setup.stats.total_refunded || 0)}`,
				icon: "💰",
				color: "emerald",
				formatted: false
			}, null, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Pending",
				value: $setup.stats.pending_refunds,
				icon: "⏳",
				color: "amber"
			}, null, 8, ["value"]),
			createVNode(_component_ModernMetricCard, {
				title: "Avg Refund",
				value: `KSh ${$setup.formatNumber($setup.stats.average_refund || 0)}`,
				icon: "📊",
				color: "purple",
				formatted: false
			}, null, 8, ["value"])
		]),
		createBaseVNode("div", _hoisted_8$7, [createVNode(_component_SearchBar, {
			modelValue: $setup.searchTerm,
			"onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => $setup.searchTerm = $event),
			placeholder: "Search refunds...",
			filters: $setup.filters,
			onFilterChange: $setup.handleFilterChange,
			onClear: $setup.clearFilters,
			"show-add-button": false
		}, null, 8, [
			"modelValue",
			"filters",
			"onFilterChange",
			"onClear"
		]), createVNode(_component_DataTable, {
			title: "Refund History",
			data: $setup.filteredRefunds,
			columns: $setup.columns,
			actions: []
		}, {
			"cell-status": withCtx(({ value }) => [createBaseVNode("span", { class: normalizeClass([value === "completed" ? "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400" : "bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400", "px-2 py-0.5 text-xs font-medium rounded-full"]) }, toDisplayString(value), 3)]),
			_: 1
		}, 8, ["data", "columns"])])
	]);
}
var Refunds_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$7, [["render", _sfc_render$7], ["__scopeId", "data-v-bb437387"]]);
var _sfc_main$6 = {
	name: "RevenueStreams",
	props: { data: {
		type: Array,
		default: () => []
	} },
	emits: ["refresh"],
	data() {
		return {
			showFormModal: false,
			showDeleteModal: false,
			selectedStream: null,
			streamToDelete: null,
			saveLoading: false,
			deleteLoading: false,
			formData: {
				name: "",
				category: "voucher_sales",
				target_revenue: 0,
				description: "",
				is_active: true
			}
		};
	},
	computed: {
		totalRevenue() {
			return this.data.reduce((sum, stream) => sum + (stream.current_revenue || 0), 0);
		},
		activeStreamsCount() {
			return this.data.filter((s) => s.is_active).length;
		},
		avgGrowth() {
			const activeStreams = this.data.filter((s) => s.is_active);
			if (activeStreams.length === 0) return 0;
			return activeStreams.reduce((sum, s) => sum + (s.growth || 0), 0) / activeStreams.length;
		},
		avgAchievement() {
			const activeStreams = this.data.filter((s) => s.is_active);
			if (activeStreams.length === 0) return 0;
			return activeStreams.reduce((sum, s) => sum + (s.achievement || 0), 0) / activeStreams.length;
		}
	},
	methods: {
		formatNumber(num) {
			return new Intl.NumberFormat("en-KE").format(num || 0);
		},
		getCategoryColor(category) {
			const colors = {
				"voucher_sales": "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
				"package_sales": "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400",
				"usage_charges": "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400",
				"premium_services": "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400",
				"ads_revenue": "bg-pink-100 text-pink-800 dark:bg-pink-900/30 dark:text-pink-400",
				"value_added": "bg-cyan-100 text-cyan-800 dark:bg-cyan-900/30 dark:text-cyan-400",
				"other": "bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-400"
			};
			return colors[category] || colors.other;
		},
		getAchievementColor(achievement) {
			if (achievement >= 100) return "bg-emerald-500";
			if (achievement >= 75) return "bg-blue-500";
			if (achievement >= 50) return "bg-amber-500";
			return "bg-red-500";
		},
		openAddModal() {
			this.selectedStream = null;
			this.formData = {
				name: "",
				category: "voucher_sales",
				target_revenue: 0,
				description: "",
				is_active: true
			};
			this.showFormModal = true;
		},
		openEditModal(stream) {
			this.selectedStream = stream;
			this.formData = {
				name: stream.name,
				category: stream.category,
				target_revenue: stream.target_revenue,
				description: stream.description || "",
				is_active: stream.is_active
			};
			this.showFormModal = true;
		},
		closeFormModal() {
			this.showFormModal = false;
			this.selectedStream = null;
		},
		async saveStream() {
			this.saveLoading = true;
			try {
				const url = this.selectedStream ? `https://srv.teralinkxwaves.uk/api/finance/api/revenue-streams/${this.selectedStream.id}/` : "https://srv.teralinkxwaves.uk/api/finance/api/revenue-streams/";
				const method = this.selectedStream ? "PUT" : "POST";
				if (!(await fetch(url, {
					method,
					headers: {
						"Content-Type": "application/json",
						"Authorization": `Bearer ${localStorage.getItem("access_token")}`
					},
					body: JSON.stringify(this.formData)
				})).ok) throw new Error("Failed to save");
				this.$emit("refresh");
				this.closeFormModal();
			} catch (error) {
				console.error("Error saving stream:", error);
				alert("Failed to save revenue stream");
			} finally {
				this.saveLoading = false;
			}
		},
		openDeleteModal(stream) {
			this.streamToDelete = stream;
			this.showDeleteModal = true;
		},
		closeDeleteModal() {
			this.showDeleteModal = false;
			this.streamToDelete = null;
		},
		async confirmDelete() {
			this.deleteLoading = true;
			try {
				if (!(await fetch(`https://srv.teralinkxwaves.uk/api/finance/api/revenue-streams/${this.streamToDelete.id}/`, {
					method: "DELETE",
					headers: { "Authorization": `Bearer ${localStorage.getItem("access_token")}` }
				})).ok) throw new Error("Failed to delete");
				this.$emit("refresh");
				this.closeDeleteModal();
			} catch (error) {
				console.error("Error deleting stream:", error);
				alert("Failed to delete revenue stream");
			} finally {
				this.deleteLoading = false;
			}
		}
	}
};
var _hoisted_1$6 = { class: "space-y-6" };
var _hoisted_2$6 = { class: "grid grid-cols-1 md:grid-cols-4 gap-4" };
var _hoisted_3$6 = { class: "bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg" };
var _hoisted_4$6 = { class: "flex items-center justify-between" };
var _hoisted_5$6 = { class: "text-3xl font-bold mt-2" };
var _hoisted_6$6 = { class: "bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl p-6 text-white shadow-lg" };
var _hoisted_7$6 = { class: "flex items-center justify-between" };
var _hoisted_8$6 = { class: "text-3xl font-bold mt-2" };
var _hoisted_9$6 = { class: "bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white shadow-lg" };
var _hoisted_10$6 = { class: "flex items-center justify-between" };
var _hoisted_11$5 = { class: "text-3xl font-bold mt-2" };
var _hoisted_12$5 = { class: "bg-gradient-to-br from-amber-500 to-amber-600 rounded-xl p-6 text-white shadow-lg" };
var _hoisted_13$5 = { class: "flex items-center justify-between" };
var _hoisted_14$5 = { class: "text-3xl font-bold mt-2" };
var _hoisted_15$5 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-lg overflow-hidden" };
var _hoisted_16$5 = { class: "p-6 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center" };
var _hoisted_17$5 = { class: "overflow-x-auto" };
var _hoisted_18$5 = { class: "w-full" };
var _hoisted_19$4 = { class: "divide-y divide-slate-200 dark:divide-slate-700" };
var _hoisted_20$4 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_21$4 = { class: "text-sm font-medium text-slate-900 dark:text-white" };
var _hoisted_22$4 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_23$4 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_24$4 = { class: "text-sm font-semibold text-slate-900 dark:text-white" };
var _hoisted_25$4 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_26$4 = { class: "text-sm text-slate-600 dark:text-slate-400" };
var _hoisted_27$4 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_28$4 = { class: "flex items-center gap-2" };
var _hoisted_29$4 = { class: "flex-1 bg-slate-200 dark:bg-slate-700 rounded-full h-2 w-24" };
var _hoisted_30$4 = { class: "text-sm font-medium text-slate-900 dark:text-white" };
var _hoisted_31$4 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_32$4 = { class: "flex items-center gap-1" };
var _hoisted_33$4 = {
	key: 0,
	class: "w-4 h-4 text-emerald-500",
	fill: "currentColor",
	viewBox: "0 0 20 20"
};
var _hoisted_34$4 = {
	key: 1,
	class: "w-4 h-4 text-red-500",
	fill: "currentColor",
	viewBox: "0 0 20 20"
};
var _hoisted_35$4 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_36$4 = {
	key: 0,
	class: "px-2 py-1 text-xs font-medium rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400"
};
var _hoisted_37$4 = {
	key: 1,
	class: "px-2 py-1 text-xs font-medium rounded-full bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-400"
};
var _hoisted_38$4 = { class: "px-6 py-4 whitespace-nowrap text-right" };
var _hoisted_39$4 = { class: "flex items-center justify-end gap-2" };
var _hoisted_40$4 = ["onClick"];
var _hoisted_41$4 = ["onClick"];
var _hoisted_42$4 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full" };
var _hoisted_43$4 = { class: "flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700" };
var _hoisted_44$4 = { class: "text-lg font-semibold text-slate-900 dark:text-white" };
var _hoisted_45$3 = { class: "p-6 space-y-4" };
var _hoisted_46$3 = { class: "grid grid-cols-2 gap-4" };
var _hoisted_47$3 = { class: "flex items-center gap-2 cursor-pointer" };
var _hoisted_48$2 = { class: "flex items-center justify-end gap-3 p-6 border-t border-slate-200 dark:border-slate-700" };
var _hoisted_49$2 = ["disabled"];
var _hoisted_50$2 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-md w-full" };
var _hoisted_51$2 = { class: "p-6" };
var _hoisted_52$1 = { class: "flex items-center gap-4" };
var _hoisted_53$1 = { class: "text-sm text-slate-600 dark:text-slate-400 mt-1" };
var _hoisted_54$1 = { class: "flex items-center justify-end gap-3 p-6 border-t border-slate-200 dark:border-slate-700" };
var _hoisted_55 = ["disabled"];
function _sfc_render$6(_ctx, _cache, $props, $setup, $data, $options) {
	return openBlock(), createElementBlock("div", _hoisted_1$6, [
		createBaseVNode("div", _hoisted_2$6, [
			createBaseVNode("div", _hoisted_3$6, [createBaseVNode("div", _hoisted_4$6, [createBaseVNode("div", null, [_cache[13] || (_cache[13] = createBaseVNode("p", { class: "text-blue-100 text-sm font-medium" }, "Total Revenue", -1)), createBaseVNode("p", _hoisted_5$6, "KES " + toDisplayString($options.formatNumber($options.totalRevenue)), 1)]), _cache[14] || (_cache[14] = createBaseVNode("svg", {
				class: "w-12 h-12 text-blue-200",
				fill: "currentColor",
				viewBox: "0 0 20 20"
			}, [createBaseVNode("path", { d: "M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" }), createBaseVNode("path", {
				"fill-rule": "evenodd",
				d: "M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z",
				"clip-rule": "evenodd"
			})], -1))])]),
			createBaseVNode("div", _hoisted_6$6, [createBaseVNode("div", _hoisted_7$6, [createBaseVNode("div", null, [_cache[15] || (_cache[15] = createBaseVNode("p", { class: "text-emerald-100 text-sm font-medium" }, "Active Streams", -1)), createBaseVNode("p", _hoisted_8$6, toDisplayString($options.activeStreamsCount), 1)]), _cache[16] || (_cache[16] = createBaseVNode("svg", {
				class: "w-12 h-12 text-emerald-200",
				fill: "currentColor",
				viewBox: "0 0 20 20"
			}, [createBaseVNode("path", {
				"fill-rule": "evenodd",
				d: "M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 0l-2 2a1 1 0 101.414 1.414L8 10.414l1.293 1.293a1 1 0 001.414 0l4-4z",
				"clip-rule": "evenodd"
			})], -1))])]),
			createBaseVNode("div", _hoisted_9$6, [createBaseVNode("div", _hoisted_10$6, [createBaseVNode("div", null, [_cache[17] || (_cache[17] = createBaseVNode("p", { class: "text-purple-100 text-sm font-medium" }, "Avg Growth", -1)), createBaseVNode("p", _hoisted_11$5, toDisplayString($options.avgGrowth.toFixed(1)) + "%", 1)]), _cache[18] || (_cache[18] = createBaseVNode("svg", {
				class: "w-12 h-12 text-purple-200",
				fill: "currentColor",
				viewBox: "0 0 20 20"
			}, [createBaseVNode("path", {
				"fill-rule": "evenodd",
				d: "M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L11 10.586 14.586 7H12z",
				"clip-rule": "evenodd"
			})], -1))])]),
			createBaseVNode("div", _hoisted_12$5, [createBaseVNode("div", _hoisted_13$5, [createBaseVNode("div", null, [_cache[19] || (_cache[19] = createBaseVNode("p", { class: "text-amber-100 text-sm font-medium" }, "Target Achievement", -1)), createBaseVNode("p", _hoisted_14$5, toDisplayString($options.avgAchievement.toFixed(0)) + "%", 1)]), _cache[20] || (_cache[20] = createBaseVNode("svg", {
				class: "w-12 h-12 text-amber-200",
				fill: "currentColor",
				viewBox: "0 0 20 20"
			}, [createBaseVNode("path", {
				"fill-rule": "evenodd",
				d: "M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z",
				"clip-rule": "evenodd"
			})], -1))])])
		]),
		createBaseVNode("div", _hoisted_15$5, [createBaseVNode("div", _hoisted_16$5, [_cache[22] || (_cache[22] = createBaseVNode("h2", { class: "text-xl font-bold text-slate-900 dark:text-white" }, "Revenue Streams", -1)), createBaseVNode("button", {
			onClick: _cache[0] || (_cache[0] = (...args) => $options.openAddModal && $options.openAddModal(...args)),
			class: "px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
		}, [..._cache[21] || (_cache[21] = [createBaseVNode("svg", {
			class: "w-4 h-4",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M12 4v16m8-8H4"
		})], -1), createTextVNode(" Add Stream ", -1)])])]), createBaseVNode("div", _hoisted_17$5, [createBaseVNode("table", _hoisted_18$5, [_cache[27] || (_cache[27] = createBaseVNode("thead", { class: "bg-slate-50 dark:bg-slate-900" }, [createBaseVNode("tr", null, [
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Name"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Category"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Current Revenue"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Target"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Achievement"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Growth"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Status"),
			createBaseVNode("th", { class: "px-6 py-3 text-right text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Actions")
		])], -1)), createBaseVNode("tbody", _hoisted_19$4, [(openBlock(true), createElementBlock(Fragment, null, renderList($props.data, (stream) => {
			return openBlock(), createElementBlock("tr", {
				key: stream.id,
				class: "hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors"
			}, [
				createBaseVNode("td", _hoisted_20$4, [createBaseVNode("div", _hoisted_21$4, toDisplayString(stream.name), 1)]),
				createBaseVNode("td", _hoisted_22$4, [createBaseVNode("span", { class: normalizeClass(["px-2 py-1 text-xs font-medium rounded-full", $options.getCategoryColor(stream.category)]) }, toDisplayString(stream.category_display), 3)]),
				createBaseVNode("td", _hoisted_23$4, [createBaseVNode("div", _hoisted_24$4, "KES " + toDisplayString($options.formatNumber(stream.current_revenue)), 1)]),
				createBaseVNode("td", _hoisted_25$4, [createBaseVNode("div", _hoisted_26$4, "KES " + toDisplayString($options.formatNumber(stream.target_revenue)), 1)]),
				createBaseVNode("td", _hoisted_27$4, [createBaseVNode("div", _hoisted_28$4, [createBaseVNode("div", _hoisted_29$4, [createBaseVNode("div", {
					class: normalizeClass(["h-2 rounded-full transition-all", $options.getAchievementColor(stream.achievement)]),
					style: normalizeStyle({ width: Math.min(stream.achievement, 100) + "%" })
				}, null, 6)]), createBaseVNode("span", _hoisted_30$4, toDisplayString(stream.achievement.toFixed(0)) + "%", 1)])]),
				createBaseVNode("td", _hoisted_31$4, [createBaseVNode("div", _hoisted_32$4, [stream.growth > 0 ? (openBlock(), createElementBlock("svg", _hoisted_33$4, [..._cache[23] || (_cache[23] = [createBaseVNode("path", {
					"fill-rule": "evenodd",
					d: "M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z",
					"clip-rule": "evenodd"
				}, null, -1)])])) : stream.growth < 0 ? (openBlock(), createElementBlock("svg", _hoisted_34$4, [..._cache[24] || (_cache[24] = [createBaseVNode("path", {
					"fill-rule": "evenodd",
					d: "M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z",
					"clip-rule": "evenodd"
				}, null, -1)])])) : createCommentVNode("", true), createBaseVNode("span", { class: normalizeClass(["text-sm font-medium", stream.growth > 0 ? "text-emerald-600 dark:text-emerald-400" : stream.growth < 0 ? "text-red-600 dark:text-red-400" : "text-slate-600 dark:text-slate-400"]) }, toDisplayString(stream.growth.toFixed(1)) + "% ", 3)])]),
				createBaseVNode("td", _hoisted_35$4, [stream.is_active ? (openBlock(), createElementBlock("span", _hoisted_36$4, " Active ")) : (openBlock(), createElementBlock("span", _hoisted_37$4, " Inactive "))]),
				createBaseVNode("td", _hoisted_38$4, [createBaseVNode("div", _hoisted_39$4, [createBaseVNode("button", {
					onClick: ($event) => $options.openEditModal(stream),
					class: "p-2 hover:bg-blue-100 dark:hover:bg-blue-600 rounded transition-colors",
					title: "Edit"
				}, [..._cache[25] || (_cache[25] = [createBaseVNode("svg", {
					class: "w-4 h-4 text-blue-600 dark:text-blue-400",
					fill: "none",
					stroke: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", {
					"stroke-linecap": "round",
					"stroke-linejoin": "round",
					"stroke-width": "2",
					d: "M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
				})], -1)])], 8, _hoisted_40$4), createBaseVNode("button", {
					onClick: ($event) => $options.openDeleteModal(stream),
					class: "p-2 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors",
					title: "Delete"
				}, [..._cache[26] || (_cache[26] = [createBaseVNode("svg", {
					class: "w-4 h-4 text-red-600 dark:text-red-400",
					fill: "none",
					stroke: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", {
					"stroke-linecap": "round",
					"stroke-linejoin": "round",
					"stroke-width": "2",
					d: "M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
				})], -1)])], 8, _hoisted_41$4)])])
			]);
		}), 128))])])])]),
		$data.showFormModal ? (openBlock(), createElementBlock("div", {
			key: 0,
			class: "fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4",
			onClick: _cache[9] || (_cache[9] = withModifiers((...args) => $options.closeFormModal && $options.closeFormModal(...args), ["self"]))
		}, [createBaseVNode("div", _hoisted_42$4, [
			createBaseVNode("div", _hoisted_43$4, [createBaseVNode("h2", _hoisted_44$4, toDisplayString($data.selectedStream ? "Edit Revenue Stream" : "Add Revenue Stream"), 1), createBaseVNode("button", {
				onClick: _cache[1] || (_cache[1] = (...args) => $options.closeFormModal && $options.closeFormModal(...args)),
				class: "p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
			}, [..._cache[28] || (_cache[28] = [createBaseVNode("svg", {
				class: "w-5 h-5",
				fill: "none",
				stroke: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M6 18L18 6M6 6l12 12"
			})], -1)])])]),
			createBaseVNode("div", _hoisted_45$3, [
				createBaseVNode("div", null, [_cache[29] || (_cache[29] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2" }, "Name *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => $data.formData.name = $event),
					type: "text",
					required: "",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $data.formData.name]])]),
				createBaseVNode("div", _hoisted_46$3, [createBaseVNode("div", null, [_cache[31] || (_cache[31] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2" }, "Category *", -1)), withDirectives(createBaseVNode("select", {
					"onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => $data.formData.category = $event),
					required: "",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, [..._cache[30] || (_cache[30] = [createStaticVNode("<option value=\"voucher_sales\">Voucher Sales</option><option value=\"package_sales\">Package Sales</option><option value=\"usage_charges\">Usage Charges</option><option value=\"premium_services\">Premium Services</option><option value=\"ads_revenue\">Ads Revenue</option><option value=\"value_added\">Value Added</option><option value=\"other\">Other</option>", 7)])], 512), [[vModelSelect, $data.formData.category]])]), createBaseVNode("div", null, [_cache[32] || (_cache[32] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2" }, "Target Revenue (KES) *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => $data.formData.target_revenue = $event),
					type: "number",
					step: "0.01",
					required: "",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $data.formData.target_revenue]])])]),
				createBaseVNode("div", null, [_cache[33] || (_cache[33] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2" }, "Description", -1)), withDirectives(createBaseVNode("textarea", {
					"onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => $data.formData.description = $event),
					rows: "3",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $data.formData.description]])]),
				createBaseVNode("div", null, [createBaseVNode("label", _hoisted_47$3, [withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => $data.formData.is_active = $event),
					type: "checkbox",
					class: "w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded"
				}, null, 512), [[vModelCheckbox, $data.formData.is_active]]), _cache[34] || (_cache[34] = createBaseVNode("span", { class: "text-sm text-slate-700 dark:text-slate-300" }, "Active Stream", -1))])])
			]),
			createBaseVNode("div", _hoisted_48$2, [createBaseVNode("button", {
				onClick: _cache[7] || (_cache[7] = (...args) => $options.closeFormModal && $options.closeFormModal(...args)),
				class: "px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg"
			}, "Cancel"), createBaseVNode("button", {
				onClick: _cache[8] || (_cache[8] = (...args) => $options.saveStream && $options.saveStream(...args)),
				disabled: $data.saveLoading,
				class: normalizeClass(["px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg", { "opacity-50": $data.saveLoading }])
			}, toDisplayString($data.saveLoading ? "Saving..." : "Save"), 11, _hoisted_49$2)])
		])])) : createCommentVNode("", true),
		$data.showDeleteModal ? (openBlock(), createElementBlock("div", {
			key: 1,
			class: "fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4",
			onClick: _cache[12] || (_cache[12] = withModifiers((...args) => $options.closeDeleteModal && $options.closeDeleteModal(...args), ["self"]))
		}, [createBaseVNode("div", _hoisted_50$2, [createBaseVNode("div", _hoisted_51$2, [createBaseVNode("div", _hoisted_52$1, [_cache[36] || (_cache[36] = createBaseVNode("div", { class: "w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center" }, [createBaseVNode("svg", {
			class: "w-6 h-6 text-red-600 dark:text-red-400",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
		})])], -1)), createBaseVNode("div", null, [_cache[35] || (_cache[35] = createBaseVNode("h3", { class: "text-lg font-semibold text-slate-900 dark:text-white" }, "Delete Revenue Stream", -1)), createBaseVNode("p", _hoisted_53$1, "Are you sure you want to delete \"" + toDisplayString($data.streamToDelete?.name) + "\"?", 1)])])]), createBaseVNode("div", _hoisted_54$1, [createBaseVNode("button", {
			onClick: _cache[10] || (_cache[10] = (...args) => $options.closeDeleteModal && $options.closeDeleteModal(...args)),
			class: "px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg"
		}, "Cancel"), createBaseVNode("button", {
			onClick: _cache[11] || (_cache[11] = (...args) => $options.confirmDelete && $options.confirmDelete(...args)),
			disabled: $data.deleteLoading,
			class: normalizeClass(["px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg", { "opacity-50": $data.deleteLoading }])
		}, toDisplayString($data.deleteLoading ? "Deleting..." : "Delete"), 11, _hoisted_55)])])])) : createCommentVNode("", true)
	]);
}
var RevenueStreams_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$6, [["render", _sfc_render$6]]);
var _sfc_main$5 = {
	name: "Expenses",
	props: { data: {
		type: Array,
		default: () => []
	} },
	emits: ["refresh"],
	data() {
		return {
			showFormModal: false,
			showDeleteModal: false,
			selectedExpense: null,
			expenseToDelete: null,
			saveLoading: false,
			deleteLoading: false,
			formData: {
				description: "",
				category: "operational",
				amount: 0,
				expense_date: (/* @__PURE__ */ new Date()).toISOString().split("T")[0],
				status: "pending"
			}
		};
	},
	computed: {
		totalExpenses() {
			return this.data.reduce((sum, exp) => sum + (exp.amount || 0), 0);
		},
		pendingCount() {
			return this.data.filter((e) => e.status === "pending").length;
		},
		paidThisMonth() {
			const now = /* @__PURE__ */ new Date();
			const thisMonth = now.getMonth();
			const thisYear = now.getFullYear();
			return this.data.filter((e) => {
				const expDate = new Date(e.expense_date);
				return e.status === "paid" && expDate.getMonth() === thisMonth && expDate.getFullYear() === thisYear;
			}).reduce((sum, e) => sum + (e.amount || 0), 0);
		}
	},
	methods: {
		formatNumber(num) {
			return new Intl.NumberFormat("en-KE").format(num || 0);
		},
		formatDate(date) {
			return new Date(date).toLocaleDateString("en-KE", {
				year: "numeric",
				month: "short",
				day: "numeric"
			});
		},
		getCategoryColor(category) {
			const colors = {
				"operational": "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
				"marketing": "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400",
				"infrastructure": "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400",
				"salaries": "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400",
				"maintenance": "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400",
				"other": "bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-400"
			};
			return colors[category] || colors.other;
		},
		getStatusColor(status) {
			const colors = {
				"pending": "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
				"approved": "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
				"paid": "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400",
				"rejected": "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400"
			};
			return colors[status] || colors.pending;
		},
		openAddModal() {
			this.selectedExpense = null;
			this.formData = {
				description: "",
				category: "operational",
				amount: 0,
				expense_date: (/* @__PURE__ */ new Date()).toISOString().split("T")[0],
				status: "pending"
			};
			this.showFormModal = true;
		},
		openEditModal(expense) {
			this.selectedExpense = expense;
			this.formData = {
				description: expense.description,
				category: expense.category,
				amount: expense.amount,
				expense_date: expense.expense_date,
				status: expense.status
			};
			this.showFormModal = true;
		},
		closeFormModal() {
			this.showFormModal = false;
			this.selectedExpense = null;
		},
		async saveExpense() {
			this.saveLoading = true;
			try {
				const url = this.selectedExpense ? `https://srv.teralinkxwaves.uk/api/finance/api/expenses/${this.selectedExpense.id}/` : "https://srv.teralinkxwaves.uk/api/finance/api/expenses/";
				const method = this.selectedExpense ? "PUT" : "POST";
				if (!(await fetch(url, {
					method,
					headers: {
						"Content-Type": "application/json",
						"Authorization": `Bearer ${localStorage.getItem("access_token")}`
					},
					body: JSON.stringify(this.formData)
				})).ok) throw new Error("Failed to save");
				this.$emit("refresh");
				this.closeFormModal();
			} catch (error) {
				console.error("Error saving expense:", error);
				alert("Failed to save expense");
			} finally {
				this.saveLoading = false;
			}
		},
		openDeleteModal(expense) {
			this.expenseToDelete = expense;
			this.showDeleteModal = true;
		},
		closeDeleteModal() {
			this.showDeleteModal = false;
			this.expenseToDelete = null;
		},
		async confirmDelete() {
			this.deleteLoading = true;
			try {
				if (!(await fetch(`https://srv.teralinkxwaves.uk/api/finance/api/expenses/${this.expenseToDelete.id}/`, {
					method: "DELETE",
					headers: { "Authorization": `Bearer ${localStorage.getItem("access_token")}` }
				})).ok) throw new Error("Failed to delete");
				this.$emit("refresh");
				this.closeDeleteModal();
			} catch (error) {
				console.error("Error deleting expense:", error);
				alert("Failed to delete expense");
			} finally {
				this.deleteLoading = false;
			}
		}
	}
};
var _hoisted_1$5 = { class: "space-y-6" };
var _hoisted_2$5 = { class: "grid grid-cols-1 md:grid-cols-4 gap-4" };
var _hoisted_3$5 = { class: "bg-gradient-to-br from-red-500 to-red-600 rounded-xl p-6 text-white shadow-lg" };
var _hoisted_4$5 = { class: "flex items-center justify-between" };
var _hoisted_5$5 = { class: "text-3xl font-bold mt-2" };
var _hoisted_6$5 = { class: "bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl p-6 text-white shadow-lg" };
var _hoisted_7$5 = { class: "flex items-center justify-between" };
var _hoisted_8$5 = { class: "text-3xl font-bold mt-2" };
var _hoisted_9$5 = { class: "bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl p-6 text-white shadow-lg" };
var _hoisted_10$5 = { class: "flex items-center justify-between" };
var _hoisted_11$4 = { class: "text-3xl font-bold mt-2" };
var _hoisted_12$4 = { class: "bg-gradient-to-br from-slate-500 to-slate-600 rounded-xl p-6 text-white shadow-lg" };
var _hoisted_13$4 = { class: "flex items-center justify-between" };
var _hoisted_14$4 = { class: "text-3xl font-bold mt-2" };
var _hoisted_15$4 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-lg overflow-hidden" };
var _hoisted_16$4 = { class: "p-6 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center" };
var _hoisted_17$4 = { class: "overflow-x-auto" };
var _hoisted_18$4 = { class: "w-full" };
var _hoisted_19$3 = { class: "divide-y divide-slate-200 dark:divide-slate-700" };
var _hoisted_20$3 = { class: "px-6 py-4" };
var _hoisted_21$3 = { class: "text-sm font-medium text-slate-900 dark:text-white" };
var _hoisted_22$3 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_23$3 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_24$3 = { class: "text-sm font-semibold text-slate-900 dark:text-white" };
var _hoisted_25$3 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_26$3 = { class: "text-sm text-slate-600 dark:text-slate-400" };
var _hoisted_27$3 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_28$3 = { class: "text-sm text-slate-600 dark:text-slate-400" };
var _hoisted_29$3 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_30$3 = { class: "px-6 py-4 whitespace-nowrap text-right" };
var _hoisted_31$3 = { class: "flex items-center justify-end gap-2" };
var _hoisted_32$3 = ["onClick"];
var _hoisted_33$3 = ["onClick"];
var _hoisted_34$3 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full" };
var _hoisted_35$3 = { class: "flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700" };
var _hoisted_36$3 = { class: "text-lg font-semibold text-slate-900 dark:text-white" };
var _hoisted_37$3 = { class: "p-6 space-y-4" };
var _hoisted_38$3 = { class: "grid grid-cols-2 gap-4" };
var _hoisted_39$3 = { class: "grid grid-cols-2 gap-4" };
var _hoisted_40$3 = { class: "flex items-center justify-end gap-3 p-6 border-t border-slate-200 dark:border-slate-700" };
var _hoisted_41$3 = ["disabled"];
var _hoisted_42$3 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-md w-full" };
var _hoisted_43$3 = { class: "flex items-center justify-end gap-3 p-6 border-t border-slate-200 dark:border-slate-700" };
var _hoisted_44$3 = ["disabled"];
function _sfc_render$5(_ctx, _cache, $props, $setup, $data, $options) {
	return openBlock(), createElementBlock("div", _hoisted_1$5, [
		createBaseVNode("div", _hoisted_2$5, [
			createBaseVNode("div", _hoisted_3$5, [createBaseVNode("div", _hoisted_4$5, [createBaseVNode("div", null, [_cache[13] || (_cache[13] = createBaseVNode("p", { class: "text-red-100 text-sm font-medium" }, "Total Expenses", -1)), createBaseVNode("p", _hoisted_5$5, "KES " + toDisplayString($options.formatNumber($options.totalExpenses)), 1)]), _cache[14] || (_cache[14] = createBaseVNode("svg", {
				class: "w-12 h-12 text-red-200",
				fill: "currentColor",
				viewBox: "0 0 20 20"
			}, [createBaseVNode("path", {
				"fill-rule": "evenodd",
				d: "M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z",
				"clip-rule": "evenodd"
			})], -1))])]),
			createBaseVNode("div", _hoisted_6$5, [createBaseVNode("div", _hoisted_7$5, [createBaseVNode("div", null, [_cache[15] || (_cache[15] = createBaseVNode("p", { class: "text-orange-100 text-sm font-medium" }, "Pending Approval", -1)), createBaseVNode("p", _hoisted_8$5, toDisplayString($options.pendingCount), 1)]), _cache[16] || (_cache[16] = createBaseVNode("svg", {
				class: "w-12 h-12 text-orange-200",
				fill: "currentColor",
				viewBox: "0 0 20 20"
			}, [createBaseVNode("path", {
				"fill-rule": "evenodd",
				d: "M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z",
				"clip-rule": "evenodd"
			})], -1))])]),
			createBaseVNode("div", _hoisted_9$5, [createBaseVNode("div", _hoisted_10$5, [createBaseVNode("div", null, [_cache[17] || (_cache[17] = createBaseVNode("p", { class: "text-emerald-100 text-sm font-medium" }, "Paid This Month", -1)), createBaseVNode("p", _hoisted_11$4, "KES " + toDisplayString($options.formatNumber($options.paidThisMonth)), 1)]), _cache[18] || (_cache[18] = createBaseVNode("svg", {
				class: "w-12 h-12 text-emerald-200",
				fill: "currentColor",
				viewBox: "0 0 20 20"
			}, [createBaseVNode("path", {
				"fill-rule": "evenodd",
				d: "M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z",
				"clip-rule": "evenodd"
			})], -1))])]),
			createBaseVNode("div", _hoisted_12$4, [createBaseVNode("div", _hoisted_13$4, [createBaseVNode("div", null, [_cache[19] || (_cache[19] = createBaseVNode("p", { class: "text-slate-100 text-sm font-medium" }, "Total Items", -1)), createBaseVNode("p", _hoisted_14$4, toDisplayString($props.data.length), 1)]), _cache[20] || (_cache[20] = createBaseVNode("svg", {
				class: "w-12 h-12 text-slate-200",
				fill: "currentColor",
				viewBox: "0 0 20 20"
			}, [createBaseVNode("path", { d: "M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" }), createBaseVNode("path", {
				"fill-rule": "evenodd",
				d: "M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z",
				"clip-rule": "evenodd"
			})], -1))])])
		]),
		createBaseVNode("div", _hoisted_15$4, [createBaseVNode("div", _hoisted_16$4, [_cache[22] || (_cache[22] = createBaseVNode("h2", { class: "text-xl font-bold text-slate-900 dark:text-white" }, "Expense Records", -1)), createBaseVNode("button", {
			onClick: _cache[0] || (_cache[0] = (...args) => $options.openAddModal && $options.openAddModal(...args)),
			class: "px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
		}, [..._cache[21] || (_cache[21] = [createBaseVNode("svg", {
			class: "w-4 h-4",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M12 4v16m8-8H4"
		})], -1), createTextVNode(" Add Expense ", -1)])])]), createBaseVNode("div", _hoisted_17$4, [createBaseVNode("table", _hoisted_18$4, [_cache[25] || (_cache[25] = createBaseVNode("thead", { class: "bg-slate-50 dark:bg-slate-900" }, [createBaseVNode("tr", null, [
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Description"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Category"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Amount"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Department"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Date"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Status"),
			createBaseVNode("th", { class: "px-6 py-3 text-right text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Actions")
		])], -1)), createBaseVNode("tbody", _hoisted_19$3, [(openBlock(true), createElementBlock(Fragment, null, renderList($props.data, (expense) => {
			return openBlock(), createElementBlock("tr", {
				key: expense.id,
				class: "hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors"
			}, [
				createBaseVNode("td", _hoisted_20$3, [createBaseVNode("div", _hoisted_21$3, toDisplayString(expense.description), 1)]),
				createBaseVNode("td", _hoisted_22$3, [createBaseVNode("span", { class: normalizeClass(["px-2 py-1 text-xs font-medium rounded-full", $options.getCategoryColor(expense.category)]) }, toDisplayString(expense.category_display), 3)]),
				createBaseVNode("td", _hoisted_23$3, [createBaseVNode("div", _hoisted_24$3, "KES " + toDisplayString($options.formatNumber(expense.amount)), 1)]),
				createBaseVNode("td", _hoisted_25$3, [createBaseVNode("div", _hoisted_26$3, toDisplayString(expense.department_name || "N/A"), 1)]),
				createBaseVNode("td", _hoisted_27$3, [createBaseVNode("div", _hoisted_28$3, toDisplayString($options.formatDate(expense.expense_date)), 1)]),
				createBaseVNode("td", _hoisted_29$3, [createBaseVNode("span", { class: normalizeClass(["px-2 py-1 text-xs font-medium rounded-full", $options.getStatusColor(expense.status)]) }, toDisplayString(expense.status_display), 3)]),
				createBaseVNode("td", _hoisted_30$3, [createBaseVNode("div", _hoisted_31$3, [createBaseVNode("button", {
					onClick: ($event) => $options.openEditModal(expense),
					class: "p-2 hover:bg-blue-100 dark:hover:bg-blue-600 rounded transition-colors",
					title: "Edit"
				}, [..._cache[23] || (_cache[23] = [createBaseVNode("svg", {
					class: "w-4 h-4 text-blue-600 dark:text-blue-400",
					fill: "none",
					stroke: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", {
					"stroke-linecap": "round",
					"stroke-linejoin": "round",
					"stroke-width": "2",
					d: "M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
				})], -1)])], 8, _hoisted_32$3), createBaseVNode("button", {
					onClick: ($event) => $options.openDeleteModal(expense),
					class: "p-2 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors",
					title: "Delete"
				}, [..._cache[24] || (_cache[24] = [createBaseVNode("svg", {
					class: "w-4 h-4 text-red-600 dark:text-red-400",
					fill: "none",
					stroke: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", {
					"stroke-linecap": "round",
					"stroke-linejoin": "round",
					"stroke-width": "2",
					d: "M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
				})], -1)])], 8, _hoisted_33$3)])])
			]);
		}), 128))])])])]),
		$data.showFormModal ? (openBlock(), createElementBlock("div", {
			key: 0,
			class: "fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4",
			onClick: _cache[9] || (_cache[9] = withModifiers((...args) => $options.closeFormModal && $options.closeFormModal(...args), ["self"]))
		}, [createBaseVNode("div", _hoisted_34$3, [
			createBaseVNode("div", _hoisted_35$3, [createBaseVNode("h2", _hoisted_36$3, toDisplayString($data.selectedExpense ? "Edit Expense" : "Add Expense"), 1), createBaseVNode("button", {
				onClick: _cache[1] || (_cache[1] = (...args) => $options.closeFormModal && $options.closeFormModal(...args)),
				class: "p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
			}, [..._cache[26] || (_cache[26] = [createBaseVNode("svg", {
				class: "w-5 h-5",
				fill: "none",
				stroke: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M6 18L18 6M6 6l12 12"
			})], -1)])])]),
			createBaseVNode("div", _hoisted_37$3, [
				createBaseVNode("div", null, [_cache[27] || (_cache[27] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2" }, "Description *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => $data.formData.description = $event),
					type: "text",
					required: "",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $data.formData.description]])]),
				createBaseVNode("div", _hoisted_38$3, [createBaseVNode("div", null, [_cache[29] || (_cache[29] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2" }, "Category *", -1)), withDirectives(createBaseVNode("select", {
					"onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => $data.formData.category = $event),
					required: "",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, [..._cache[28] || (_cache[28] = [createStaticVNode("<option value=\"operational\">Operational</option><option value=\"marketing\">Marketing</option><option value=\"infrastructure\">Infrastructure</option><option value=\"salaries\">Salaries</option><option value=\"maintenance\">Maintenance</option><option value=\"other\">Other</option>", 6)])], 512), [[vModelSelect, $data.formData.category]])]), createBaseVNode("div", null, [_cache[30] || (_cache[30] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2" }, "Amount (KES) *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => $data.formData.amount = $event),
					type: "number",
					step: "0.01",
					required: "",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $data.formData.amount]])])]),
				createBaseVNode("div", _hoisted_39$3, [createBaseVNode("div", null, [_cache[31] || (_cache[31] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2" }, "Expense Date *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => $data.formData.expense_date = $event),
					type: "date",
					required: "",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $data.formData.expense_date]])]), createBaseVNode("div", null, [_cache[33] || (_cache[33] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2" }, "Status *", -1)), withDirectives(createBaseVNode("select", {
					"onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => $data.formData.status = $event),
					required: "",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, [..._cache[32] || (_cache[32] = [
					createBaseVNode("option", { value: "pending" }, "Pending", -1),
					createBaseVNode("option", { value: "approved" }, "Approved", -1),
					createBaseVNode("option", { value: "paid" }, "Paid", -1),
					createBaseVNode("option", { value: "rejected" }, "Rejected", -1)
				])], 512), [[vModelSelect, $data.formData.status]])])])
			]),
			createBaseVNode("div", _hoisted_40$3, [createBaseVNode("button", {
				onClick: _cache[7] || (_cache[7] = (...args) => $options.closeFormModal && $options.closeFormModal(...args)),
				class: "px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg"
			}, "Cancel"), createBaseVNode("button", {
				onClick: _cache[8] || (_cache[8] = (...args) => $options.saveExpense && $options.saveExpense(...args)),
				disabled: $data.saveLoading,
				class: normalizeClass(["px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg", { "opacity-50": $data.saveLoading }])
			}, toDisplayString($data.saveLoading ? "Saving..." : "Save"), 11, _hoisted_41$3)])
		])])) : createCommentVNode("", true),
		$data.showDeleteModal ? (openBlock(), createElementBlock("div", {
			key: 1,
			class: "fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4",
			onClick: _cache[12] || (_cache[12] = withModifiers((...args) => $options.closeDeleteModal && $options.closeDeleteModal(...args), ["self"]))
		}, [createBaseVNode("div", _hoisted_42$3, [_cache[34] || (_cache[34] = createStaticVNode("<div class=\"p-6\"><div class=\"flex items-center gap-4\"><div class=\"w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center\"><svg class=\"w-6 h-6 text-red-600 dark:text-red-400\" fill=\"none\" stroke=\"currentColor\" viewBox=\"0 0 24 24\"><path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z\"></path></svg></div><div><h3 class=\"text-lg font-semibold text-slate-900 dark:text-white\">Delete Expense</h3><p class=\"text-sm text-slate-600 dark:text-slate-400 mt-1\">Are you sure you want to delete this expense?</p></div></div></div>", 1)), createBaseVNode("div", _hoisted_43$3, [createBaseVNode("button", {
			onClick: _cache[10] || (_cache[10] = (...args) => $options.closeDeleteModal && $options.closeDeleteModal(...args)),
			class: "px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg"
		}, "Cancel"), createBaseVNode("button", {
			onClick: _cache[11] || (_cache[11] = (...args) => $options.confirmDelete && $options.confirmDelete(...args)),
			disabled: $data.deleteLoading,
			class: normalizeClass(["px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg", { "opacity-50": $data.deleteLoading }])
		}, toDisplayString($data.deleteLoading ? "Deleting..." : "Delete"), 11, _hoisted_44$3)])])])) : createCommentVNode("", true)
	]);
}
var Expenses_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$5, [["render", _sfc_render$5]]);
var _sfc_main$4 = {
	name: "Investments",
	props: { data: {
		type: Array,
		default: () => []
	} },
	emits: ["refresh"],
	data() {
		return {
			showFormModal: false,
			showDeleteModal: false,
			selectedInvestment: null,
			investmentToDelete: null,
			saveLoading: false,
			deleteLoading: false,
			formData: {
				name: "",
				investment_type: "equity",
				amount: 0,
				current_value: 0,
				investment_date: (/* @__PURE__ */ new Date()).toISOString().split("T")[0],
				status: "active"
			}
		};
	},
	computed: {
		totalInvested() {
			return this.data.reduce((sum, inv) => sum + (inv.amount || 0), 0);
		},
		currentValue() {
			return this.data.reduce((sum, inv) => sum + (inv.current_value || 0), 0);
		},
		avgROI() {
			if (this.data.length === 0) return 0;
			return this.data.reduce((sum, inv) => sum + (inv.roi || 0), 0) / this.data.length;
		},
		activeCount() {
			return this.data.filter((i) => i.status === "active").length;
		}
	},
	methods: {
		formatNumber(num) {
			return new Intl.NumberFormat("en-KE").format(num || 0);
		},
		formatDate(date) {
			return new Date(date).toLocaleDateString("en-KE", {
				year: "numeric",
				month: "short",
				day: "numeric"
			});
		},
		getTypeColor(type) {
			const colors = {
				"equity": "bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-400",
				"debt": "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400",
				"infrastructure": "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400",
				"technology": "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
				"other": "bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-400"
			};
			return colors[type] || colors.other;
		},
		getStatusColor(status) {
			const colors = {
				"active": "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400",
				"matured": "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
				"liquidated": "bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-400"
			};
			return colors[status] || colors.active;
		},
		openAddModal() {
			this.selectedInvestment = null;
			this.formData = {
				name: "",
				investment_type: "equity",
				amount: 0,
				current_value: 0,
				investment_date: (/* @__PURE__ */ new Date()).toISOString().split("T")[0],
				status: "active"
			};
			this.showFormModal = true;
		},
		openEditModal(investment) {
			this.selectedInvestment = investment;
			this.formData = {
				name: investment.name,
				investment_type: investment.investment_type,
				amount: investment.amount,
				current_value: investment.current_value,
				investment_date: investment.investment_date,
				status: investment.status
			};
			this.showFormModal = true;
		},
		closeFormModal() {
			this.showFormModal = false;
			this.selectedInvestment = null;
		},
		async saveInvestment() {
			this.saveLoading = true;
			try {
				const url = this.selectedInvestment ? `https://srv.teralinkxwaves.uk/api/finance/api/investments/${this.selectedInvestment.id}/` : "https://srv.teralinkxwaves.uk/api/finance/api/investments/";
				const method = this.selectedInvestment ? "PUT" : "POST";
				if (!(await fetch(url, {
					method,
					headers: {
						"Content-Type": "application/json",
						"Authorization": `Bearer ${localStorage.getItem("access_token")}`
					},
					body: JSON.stringify(this.formData)
				})).ok) throw new Error("Failed to save");
				this.$emit("refresh");
				this.closeFormModal();
			} catch (error) {
				console.error("Error saving investment:", error);
				alert("Failed to save investment");
			} finally {
				this.saveLoading = false;
			}
		},
		openDeleteModal(investment) {
			this.investmentToDelete = investment;
			this.showDeleteModal = true;
		},
		closeDeleteModal() {
			this.showDeleteModal = false;
			this.investmentToDelete = null;
		},
		async confirmDelete() {
			this.deleteLoading = true;
			try {
				if (!(await fetch(`https://srv.teralinkxwaves.uk/api/finance/api/investments/${this.investmentToDelete.id}/`, {
					method: "DELETE",
					headers: { "Authorization": `Bearer ${localStorage.getItem("access_token")}` }
				})).ok) throw new Error("Failed to delete");
				this.$emit("refresh");
				this.closeDeleteModal();
			} catch (error) {
				console.error("Error deleting investment:", error);
				alert("Failed to delete investment");
			} finally {
				this.deleteLoading = false;
			}
		}
	}
};
var _hoisted_1$4 = { class: "space-y-6" };
var _hoisted_2$4 = { class: "grid grid-cols-1 md:grid-cols-4 gap-4" };
var _hoisted_3$4 = { class: "bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-xl p-6 text-white shadow-lg" };
var _hoisted_4$4 = { class: "flex items-center justify-between" };
var _hoisted_5$4 = { class: "text-3xl font-bold mt-2" };
var _hoisted_6$4 = { class: "bg-gradient-to-br from-teal-500 to-teal-600 rounded-xl p-6 text-white shadow-lg" };
var _hoisted_7$4 = { class: "flex items-center justify-between" };
var _hoisted_8$4 = { class: "text-3xl font-bold mt-2" };
var _hoisted_9$4 = { class: "bg-gradient-to-br from-cyan-500 to-cyan-600 rounded-xl p-6 text-white shadow-lg" };
var _hoisted_10$4 = { class: "flex items-center justify-between" };
var _hoisted_11$3 = { class: "text-3xl font-bold mt-2" };
var _hoisted_12$3 = { class: "bg-gradient-to-br from-violet-500 to-violet-600 rounded-xl p-6 text-white shadow-lg" };
var _hoisted_13$3 = { class: "flex items-center justify-between" };
var _hoisted_14$3 = { class: "text-3xl font-bold mt-2" };
var _hoisted_15$3 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-lg overflow-hidden" };
var _hoisted_16$3 = { class: "p-6 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center" };
var _hoisted_17$3 = { class: "overflow-x-auto" };
var _hoisted_18$3 = { class: "w-full" };
var _hoisted_19$2 = { class: "divide-y divide-slate-200 dark:divide-slate-700" };
var _hoisted_20$2 = { class: "px-6 py-4" };
var _hoisted_21$2 = { class: "text-sm font-medium text-slate-900 dark:text-white" };
var _hoisted_22$2 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_23$2 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_24$2 = { class: "text-sm font-semibold text-slate-900 dark:text-white" };
var _hoisted_25$2 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_26$2 = { class: "text-sm font-semibold text-slate-900 dark:text-white" };
var _hoisted_27$2 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_28$2 = { class: "flex items-center gap-1" };
var _hoisted_29$2 = {
	key: 0,
	class: "w-4 h-4 text-emerald-500",
	fill: "currentColor",
	viewBox: "0 0 20 20"
};
var _hoisted_30$2 = {
	key: 1,
	class: "w-4 h-4 text-red-500",
	fill: "currentColor",
	viewBox: "0 0 20 20"
};
var _hoisted_31$2 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_32$2 = { class: "text-sm text-slate-600 dark:text-slate-400" };
var _hoisted_33$2 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_34$2 = { class: "px-6 py-4 whitespace-nowrap text-right" };
var _hoisted_35$2 = { class: "flex items-center justify-end gap-2" };
var _hoisted_36$2 = ["onClick"];
var _hoisted_37$2 = ["onClick"];
var _hoisted_38$2 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full" };
var _hoisted_39$2 = { class: "flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700" };
var _hoisted_40$2 = { class: "text-lg font-semibold text-slate-900 dark:text-white" };
var _hoisted_41$2 = { class: "p-6 space-y-4" };
var _hoisted_42$2 = { class: "grid grid-cols-2 gap-4" };
var _hoisted_43$2 = { class: "grid grid-cols-2 gap-4" };
var _hoisted_44$2 = { class: "flex items-center justify-end gap-3 p-6 border-t border-slate-200 dark:border-slate-700" };
var _hoisted_45$2 = ["disabled"];
var _hoisted_46$2 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-md w-full" };
var _hoisted_47$2 = { class: "p-6" };
var _hoisted_48$1 = { class: "flex items-center gap-4" };
var _hoisted_49$1 = { class: "text-sm text-slate-600 dark:text-slate-400 mt-1" };
var _hoisted_50$1 = { class: "flex items-center justify-end gap-3 p-6 border-t border-slate-200 dark:border-slate-700" };
var _hoisted_51$1 = ["disabled"];
function _sfc_render$4(_ctx, _cache, $props, $setup, $data, $options) {
	return openBlock(), createElementBlock("div", _hoisted_1$4, [
		createBaseVNode("div", _hoisted_2$4, [
			createBaseVNode("div", _hoisted_3$4, [createBaseVNode("div", _hoisted_4$4, [createBaseVNode("div", null, [_cache[14] || (_cache[14] = createBaseVNode("p", { class: "text-indigo-100 text-sm font-medium" }, "Total Invested", -1)), createBaseVNode("p", _hoisted_5$4, "KES " + toDisplayString($options.formatNumber($options.totalInvested)), 1)]), _cache[15] || (_cache[15] = createBaseVNode("svg", {
				class: "w-12 h-12 text-indigo-200",
				fill: "currentColor",
				viewBox: "0 0 20 20"
			}, [createBaseVNode("path", { d: "M3 1a1 1 0 000 2h1.22l.305 1.222a.997.997 0 00.01.042l1.358 5.43-.893.892C3.74 11.846 4.632 14 6.414 14H15a1 1 0 000-2H6.414l1-1H14a1 1 0 00.894-.553l3-6A1 1 0 0017 3H6.28l-.31-1.243A1 1 0 005 1H3zM16 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM6.5 18a1.5 1.5 0 100-3 1.5 1.5 0 000 3z" })], -1))])]),
			createBaseVNode("div", _hoisted_6$4, [createBaseVNode("div", _hoisted_7$4, [createBaseVNode("div", null, [_cache[16] || (_cache[16] = createBaseVNode("p", { class: "text-teal-100 text-sm font-medium" }, "Current Value", -1)), createBaseVNode("p", _hoisted_8$4, "KES " + toDisplayString($options.formatNumber($options.currentValue)), 1)]), _cache[17] || (_cache[17] = createBaseVNode("svg", {
				class: "w-12 h-12 text-teal-200",
				fill: "currentColor",
				viewBox: "0 0 20 20"
			}, [createBaseVNode("path", {
				"fill-rule": "evenodd",
				d: "M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L11 10.586 14.586 7H12z",
				"clip-rule": "evenodd"
			})], -1))])]),
			createBaseVNode("div", _hoisted_9$4, [createBaseVNode("div", _hoisted_10$4, [createBaseVNode("div", null, [_cache[18] || (_cache[18] = createBaseVNode("p", { class: "text-cyan-100 text-sm font-medium" }, "Total ROI", -1)), createBaseVNode("p", _hoisted_11$3, toDisplayString($options.avgROI.toFixed(1)) + "%", 1)]), _cache[19] || (_cache[19] = createBaseVNode("svg", {
				class: "w-12 h-12 text-cyan-200",
				fill: "currentColor",
				viewBox: "0 0 20 20"
			}, [createBaseVNode("path", {
				"fill-rule": "evenodd",
				d: "M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z",
				"clip-rule": "evenodd"
			})], -1))])]),
			createBaseVNode("div", _hoisted_12$3, [createBaseVNode("div", _hoisted_13$3, [createBaseVNode("div", null, [_cache[20] || (_cache[20] = createBaseVNode("p", { class: "text-violet-100 text-sm font-medium" }, "Active Investments", -1)), createBaseVNode("p", _hoisted_14$3, toDisplayString($options.activeCount), 1)]), _cache[21] || (_cache[21] = createBaseVNode("svg", {
				class: "w-12 h-12 text-violet-200",
				fill: "currentColor",
				viewBox: "0 0 20 20"
			}, [createBaseVNode("path", {
				"fill-rule": "evenodd",
				d: "M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z",
				"clip-rule": "evenodd"
			})], -1))])])
		]),
		createBaseVNode("div", _hoisted_15$3, [createBaseVNode("div", _hoisted_16$3, [_cache[23] || (_cache[23] = createBaseVNode("h2", { class: "text-xl font-bold text-slate-900 dark:text-white" }, "Investment Portfolio", -1)), createBaseVNode("button", {
			onClick: _cache[0] || (_cache[0] = (...args) => $options.openAddModal && $options.openAddModal(...args)),
			class: "px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
		}, [..._cache[22] || (_cache[22] = [createBaseVNode("svg", {
			class: "w-4 h-4",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M12 4v16m8-8H4"
		})], -1), createTextVNode(" Add Investment ", -1)])])]), createBaseVNode("div", _hoisted_17$3, [createBaseVNode("table", _hoisted_18$3, [_cache[28] || (_cache[28] = createBaseVNode("thead", { class: "bg-slate-50 dark:bg-slate-900" }, [createBaseVNode("tr", null, [
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Name"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Type"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Amount"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Current Value"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "ROI"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Date"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Status"),
			createBaseVNode("th", { class: "px-6 py-3 text-right text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Actions")
		])], -1)), createBaseVNode("tbody", _hoisted_19$2, [(openBlock(true), createElementBlock(Fragment, null, renderList($props.data, (investment) => {
			return openBlock(), createElementBlock("tr", {
				key: investment.id,
				class: "hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors"
			}, [
				createBaseVNode("td", _hoisted_20$2, [createBaseVNode("div", _hoisted_21$2, toDisplayString(investment.name), 1)]),
				createBaseVNode("td", _hoisted_22$2, [createBaseVNode("span", { class: normalizeClass(["px-2 py-1 text-xs font-medium rounded-full", $options.getTypeColor(investment.investment_type)]) }, toDisplayString(investment.type_display), 3)]),
				createBaseVNode("td", _hoisted_23$2, [createBaseVNode("div", _hoisted_24$2, "KES " + toDisplayString($options.formatNumber(investment.amount)), 1)]),
				createBaseVNode("td", _hoisted_25$2, [createBaseVNode("div", _hoisted_26$2, "KES " + toDisplayString($options.formatNumber(investment.current_value)), 1)]),
				createBaseVNode("td", _hoisted_27$2, [createBaseVNode("div", _hoisted_28$2, [investment.roi > 0 ? (openBlock(), createElementBlock("svg", _hoisted_29$2, [..._cache[24] || (_cache[24] = [createBaseVNode("path", {
					"fill-rule": "evenodd",
					d: "M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z",
					"clip-rule": "evenodd"
				}, null, -1)])])) : investment.roi < 0 ? (openBlock(), createElementBlock("svg", _hoisted_30$2, [..._cache[25] || (_cache[25] = [createBaseVNode("path", {
					"fill-rule": "evenodd",
					d: "M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z",
					"clip-rule": "evenodd"
				}, null, -1)])])) : createCommentVNode("", true), createBaseVNode("span", { class: normalizeClass(["text-sm font-medium", investment.roi > 0 ? "text-emerald-600 dark:text-emerald-400" : investment.roi < 0 ? "text-red-600 dark:text-red-400" : "text-slate-600 dark:text-slate-400"]) }, toDisplayString(investment.roi.toFixed(1)) + "% ", 3)])]),
				createBaseVNode("td", _hoisted_31$2, [createBaseVNode("div", _hoisted_32$2, toDisplayString($options.formatDate(investment.investment_date)), 1)]),
				createBaseVNode("td", _hoisted_33$2, [createBaseVNode("span", { class: normalizeClass(["px-2 py-1 text-xs font-medium rounded-full", $options.getStatusColor(investment.status)]) }, toDisplayString(investment.status_display), 3)]),
				createBaseVNode("td", _hoisted_34$2, [createBaseVNode("div", _hoisted_35$2, [createBaseVNode("button", {
					onClick: ($event) => $options.openEditModal(investment),
					class: "p-2 hover:bg-blue-100 dark:hover:bg-blue-600 rounded transition-colors",
					title: "Edit"
				}, [..._cache[26] || (_cache[26] = [createBaseVNode("svg", {
					class: "w-4 h-4 text-blue-600 dark:text-blue-400",
					fill: "none",
					stroke: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", {
					"stroke-linecap": "round",
					"stroke-linejoin": "round",
					"stroke-width": "2",
					d: "M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
				})], -1)])], 8, _hoisted_36$2), createBaseVNode("button", {
					onClick: ($event) => $options.openDeleteModal(investment),
					class: "p-2 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors",
					title: "Delete"
				}, [..._cache[27] || (_cache[27] = [createBaseVNode("svg", {
					class: "w-4 h-4 text-red-600 dark:text-red-400",
					fill: "none",
					stroke: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", {
					"stroke-linecap": "round",
					"stroke-linejoin": "round",
					"stroke-width": "2",
					d: "M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
				})], -1)])], 8, _hoisted_37$2)])])
			]);
		}), 128))])])])]),
		$data.showFormModal ? (openBlock(), createElementBlock("div", {
			key: 0,
			class: "fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4",
			onClick: _cache[10] || (_cache[10] = withModifiers((...args) => $options.closeFormModal && $options.closeFormModal(...args), ["self"]))
		}, [createBaseVNode("div", _hoisted_38$2, [
			createBaseVNode("div", _hoisted_39$2, [createBaseVNode("h2", _hoisted_40$2, toDisplayString($data.selectedInvestment ? "Edit Investment" : "Add Investment"), 1), createBaseVNode("button", {
				onClick: _cache[1] || (_cache[1] = (...args) => $options.closeFormModal && $options.closeFormModal(...args)),
				class: "p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
			}, [..._cache[29] || (_cache[29] = [createBaseVNode("svg", {
				class: "w-5 h-5",
				fill: "none",
				stroke: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M6 18L18 6M6 6l12 12"
			})], -1)])])]),
			createBaseVNode("div", _hoisted_41$2, [
				createBaseVNode("div", null, [_cache[30] || (_cache[30] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2" }, "Name *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => $data.formData.name = $event),
					type: "text",
					required: "",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $data.formData.name]])]),
				createBaseVNode("div", _hoisted_42$2, [createBaseVNode("div", null, [_cache[32] || (_cache[32] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2" }, "Type *", -1)), withDirectives(createBaseVNode("select", {
					"onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => $data.formData.investment_type = $event),
					required: "",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, [..._cache[31] || (_cache[31] = [createStaticVNode("<option value=\"equity\">Equity</option><option value=\"debt\">Debt</option><option value=\"infrastructure\">Infrastructure</option><option value=\"technology\">Technology</option><option value=\"other\">Other</option>", 5)])], 512), [[vModelSelect, $data.formData.investment_type]])]), createBaseVNode("div", null, [_cache[33] || (_cache[33] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2" }, "Amount (KES) *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => $data.formData.amount = $event),
					type: "number",
					step: "0.01",
					required: "",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $data.formData.amount]])])]),
				createBaseVNode("div", _hoisted_43$2, [createBaseVNode("div", null, [_cache[34] || (_cache[34] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2" }, "Current Value (KES) *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => $data.formData.current_value = $event),
					type: "number",
					step: "0.01",
					required: "",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $data.formData.current_value]])]), createBaseVNode("div", null, [_cache[35] || (_cache[35] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2" }, "Investment Date *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[6] || (_cache[6] = ($event) => $data.formData.investment_date = $event),
					type: "date",
					required: "",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $data.formData.investment_date]])])]),
				createBaseVNode("div", null, [_cache[37] || (_cache[37] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2" }, "Status *", -1)), withDirectives(createBaseVNode("select", {
					"onUpdate:modelValue": _cache[7] || (_cache[7] = ($event) => $data.formData.status = $event),
					required: "",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, [..._cache[36] || (_cache[36] = [
					createBaseVNode("option", { value: "active" }, "Active", -1),
					createBaseVNode("option", { value: "matured" }, "Matured", -1),
					createBaseVNode("option", { value: "liquidated" }, "Liquidated", -1)
				])], 512), [[vModelSelect, $data.formData.status]])])
			]),
			createBaseVNode("div", _hoisted_44$2, [createBaseVNode("button", {
				onClick: _cache[8] || (_cache[8] = (...args) => $options.closeFormModal && $options.closeFormModal(...args)),
				class: "px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg"
			}, "Cancel"), createBaseVNode("button", {
				onClick: _cache[9] || (_cache[9] = (...args) => $options.saveInvestment && $options.saveInvestment(...args)),
				disabled: $data.saveLoading,
				class: normalizeClass(["px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg", { "opacity-50": $data.saveLoading }])
			}, toDisplayString($data.saveLoading ? "Saving..." : "Save"), 11, _hoisted_45$2)])
		])])) : createCommentVNode("", true),
		$data.showDeleteModal ? (openBlock(), createElementBlock("div", {
			key: 1,
			class: "fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4",
			onClick: _cache[13] || (_cache[13] = withModifiers((...args) => $options.closeDeleteModal && $options.closeDeleteModal(...args), ["self"]))
		}, [createBaseVNode("div", _hoisted_46$2, [createBaseVNode("div", _hoisted_47$2, [createBaseVNode("div", _hoisted_48$1, [_cache[39] || (_cache[39] = createBaseVNode("div", { class: "w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center" }, [createBaseVNode("svg", {
			class: "w-6 h-6 text-red-600 dark:text-red-400",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
		})])], -1)), createBaseVNode("div", null, [_cache[38] || (_cache[38] = createBaseVNode("h3", { class: "text-lg font-semibold text-slate-900 dark:text-white" }, "Delete Investment", -1)), createBaseVNode("p", _hoisted_49$1, "Are you sure you want to delete \"" + toDisplayString($data.investmentToDelete?.name) + "\"?", 1)])])]), createBaseVNode("div", _hoisted_50$1, [createBaseVNode("button", {
			onClick: _cache[11] || (_cache[11] = (...args) => $options.closeDeleteModal && $options.closeDeleteModal(...args)),
			class: "px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg"
		}, "Cancel"), createBaseVNode("button", {
			onClick: _cache[12] || (_cache[12] = (...args) => $options.confirmDelete && $options.confirmDelete(...args)),
			disabled: $data.deleteLoading,
			class: normalizeClass(["px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg", { "opacity-50": $data.deleteLoading }])
		}, toDisplayString($data.deleteLoading ? "Deleting..." : "Delete"), 11, _hoisted_51$1)])])])) : createCommentVNode("", true)
	]);
}
var Investments_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$4, [["render", _sfc_render$4]]);
var _sfc_main$3 = {
	name: "Departments",
	props: { data: {
		type: Array,
		default: () => []
	} },
	emits: ["refresh"],
	data() {
		return {
			showFormModal: false,
			showDeleteModal: false,
			selectedDepartment: null,
			departmentToDelete: null,
			saveLoading: false,
			deleteLoading: false,
			formData: {
				name: "",
				code: "",
				budget: 0,
				is_active: true
			}
		};
	},
	computed: {
		totalBudget() {
			return this.data.reduce((sum, dept) => sum + (dept.budget || 0), 0);
		},
		totalSpent() {
			return this.data.reduce((sum, dept) => sum + (dept.spent || 0), 0);
		},
		avgUtilization() {
			if (this.data.length === 0) return 0;
			return this.data.reduce((sum, dept) => sum + (dept.utilization || 0), 0) / this.data.length;
		},
		activeCount() {
			return this.data.filter((d) => d.is_active).length;
		}
	},
	methods: {
		formatNumber(num) {
			return new Intl.NumberFormat("en-KE").format(num || 0);
		},
		getUtilizationColor(utilization) {
			if (utilization >= 90) return "bg-red-500";
			if (utilization >= 75) return "bg-amber-500";
			if (utilization >= 50) return "bg-blue-500";
			return "bg-emerald-500";
		},
		openAddModal() {
			this.selectedDepartment = null;
			this.formData = {
				name: "",
				code: "",
				budget: 0,
				is_active: true
			};
			this.showFormModal = true;
		},
		openEditModal(dept) {
			this.selectedDepartment = dept;
			this.formData = {
				name: dept.name,
				code: dept.code,
				budget: dept.budget,
				is_active: dept.is_active
			};
			this.showFormModal = true;
		},
		closeFormModal() {
			this.showFormModal = false;
			this.selectedDepartment = null;
		},
		async saveDepartment() {
			this.saveLoading = true;
			try {
				const url = this.selectedDepartment ? `https://srv.teralinkxwaves.uk/api/finance/api/departments/${this.selectedDepartment.id}/` : "https://srv.teralinkxwaves.uk/api/finance/api/departments/";
				const method = this.selectedDepartment ? "PUT" : "POST";
				if (!(await fetch(url, {
					method,
					headers: {
						"Content-Type": "application/json",
						"Authorization": `Bearer ${localStorage.getItem("access_token")}`
					},
					body: JSON.stringify(this.formData)
				})).ok) throw new Error("Failed to save");
				this.$emit("refresh");
				this.closeFormModal();
			} catch (error) {
				console.error("Error saving department:", error);
				alert("Failed to save department");
			} finally {
				this.saveLoading = false;
			}
		},
		openDeleteModal(dept) {
			this.departmentToDelete = dept;
			this.showDeleteModal = true;
		},
		closeDeleteModal() {
			this.showDeleteModal = false;
			this.departmentToDelete = null;
		},
		async confirmDelete() {
			this.deleteLoading = true;
			try {
				if (!(await fetch(`https://srv.teralinkxwaves.uk/api/finance/api/departments/${this.departmentToDelete.id}/`, {
					method: "DELETE",
					headers: { "Authorization": `Bearer ${localStorage.getItem("access_token")}` }
				})).ok) throw new Error("Failed to delete");
				this.$emit("refresh");
				this.closeDeleteModal();
			} catch (error) {
				console.error("Error deleting department:", error);
				alert("Failed to delete department");
			} finally {
				this.deleteLoading = false;
			}
		}
	}
};
var _hoisted_1$3 = { class: "space-y-6" };
var _hoisted_2$3 = { class: "grid grid-cols-1 md:grid-cols-4 gap-4" };
var _hoisted_3$3 = { class: "bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg" };
var _hoisted_4$3 = { class: "flex items-center justify-between" };
var _hoisted_5$3 = { class: "text-3xl font-bold mt-2" };
var _hoisted_6$3 = { class: "bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white shadow-lg" };
var _hoisted_7$3 = { class: "flex items-center justify-between" };
var _hoisted_8$3 = { class: "text-3xl font-bold mt-2" };
var _hoisted_9$3 = { class: "bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl p-6 text-white shadow-lg" };
var _hoisted_10$3 = { class: "flex items-center justify-between" };
var _hoisted_11$2 = { class: "text-3xl font-bold mt-2" };
var _hoisted_12$2 = { class: "bg-gradient-to-br from-amber-500 to-amber-600 rounded-xl p-6 text-white shadow-lg" };
var _hoisted_13$2 = { class: "flex items-center justify-between" };
var _hoisted_14$2 = { class: "text-3xl font-bold mt-2" };
var _hoisted_15$2 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-lg overflow-hidden" };
var _hoisted_16$2 = { class: "p-6 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center" };
var _hoisted_17$2 = { class: "overflow-x-auto" };
var _hoisted_18$2 = { class: "w-full" };
var _hoisted_19$1 = { class: "divide-y divide-slate-200 dark:divide-slate-700" };
var _hoisted_20$1 = { class: "px-6 py-4" };
var _hoisted_21$1 = { class: "text-sm font-medium text-slate-900 dark:text-white" };
var _hoisted_22$1 = { class: "text-xs text-slate-500 dark:text-slate-400" };
var _hoisted_23$1 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_24$1 = { class: "text-sm text-slate-600 dark:text-slate-400" };
var _hoisted_25$1 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_26$1 = { class: "text-sm font-semibold text-slate-900 dark:text-white" };
var _hoisted_27$1 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_28$1 = { class: "text-sm font-semibold text-slate-900 dark:text-white" };
var _hoisted_29$1 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_30$1 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_31$1 = { class: "flex items-center gap-2" };
var _hoisted_32$1 = { class: "flex-1 bg-slate-200 dark:bg-slate-700 rounded-full h-2 w-24" };
var _hoisted_33$1 = { class: "text-sm font-medium text-slate-900 dark:text-white" };
var _hoisted_34$1 = { class: "px-6 py-4 whitespace-nowrap" };
var _hoisted_35$1 = {
	key: 0,
	class: "px-2 py-1 text-xs font-medium rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400"
};
var _hoisted_36$1 = {
	key: 1,
	class: "px-2 py-1 text-xs font-medium rounded-full bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-400"
};
var _hoisted_37$1 = { class: "px-6 py-4 whitespace-nowrap text-right" };
var _hoisted_38$1 = { class: "flex items-center justify-end gap-2" };
var _hoisted_39$1 = ["onClick"];
var _hoisted_40$1 = ["onClick"];
var _hoisted_41$1 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-2xl w-full" };
var _hoisted_42$1 = { class: "flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700" };
var _hoisted_43$1 = { class: "text-lg font-semibold text-slate-900 dark:text-white" };
var _hoisted_44$1 = { class: "p-6 space-y-4" };
var _hoisted_45$1 = { class: "grid grid-cols-2 gap-4" };
var _hoisted_46$1 = { class: "flex items-center gap-2 cursor-pointer" };
var _hoisted_47$1 = { class: "flex items-center justify-end gap-3 p-6 border-t border-slate-200 dark:border-slate-700" };
var _hoisted_48 = ["disabled"];
var _hoisted_49 = { class: "bg-white dark:bg-slate-800 rounded-xl shadow-2xl max-w-md w-full" };
var _hoisted_50 = { class: "p-6" };
var _hoisted_51 = { class: "flex items-center gap-4" };
var _hoisted_52 = { class: "text-sm text-slate-600 dark:text-slate-400 mt-1" };
var _hoisted_53 = { class: "flex items-center justify-end gap-3 p-6 border-t border-slate-200 dark:border-slate-700" };
var _hoisted_54 = ["disabled"];
function _sfc_render$3(_ctx, _cache, $props, $setup, $data, $options) {
	return openBlock(), createElementBlock("div", _hoisted_1$3, [
		createBaseVNode("div", _hoisted_2$3, [
			createBaseVNode("div", _hoisted_3$3, [createBaseVNode("div", _hoisted_4$3, [createBaseVNode("div", null, [_cache[12] || (_cache[12] = createBaseVNode("p", { class: "text-blue-100 text-sm font-medium" }, "Total Budget", -1)), createBaseVNode("p", _hoisted_5$3, "KES " + toDisplayString($options.formatNumber($options.totalBudget)), 1)]), _cache[13] || (_cache[13] = createBaseVNode("svg", {
				class: "w-12 h-12 text-blue-200",
				fill: "currentColor",
				viewBox: "0 0 20 20"
			}, [createBaseVNode("path", {
				"fill-rule": "evenodd",
				d: "M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z",
				"clip-rule": "evenodd"
			})], -1))])]),
			createBaseVNode("div", _hoisted_6$3, [createBaseVNode("div", _hoisted_7$3, [createBaseVNode("div", null, [_cache[14] || (_cache[14] = createBaseVNode("p", { class: "text-purple-100 text-sm font-medium" }, "Total Spent", -1)), createBaseVNode("p", _hoisted_8$3, "KES " + toDisplayString($options.formatNumber($options.totalSpent)), 1)]), _cache[15] || (_cache[15] = createBaseVNode("svg", {
				class: "w-12 h-12 text-purple-200",
				fill: "currentColor",
				viewBox: "0 0 20 20"
			}, [createBaseVNode("path", { d: "M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" }), createBaseVNode("path", {
				"fill-rule": "evenodd",
				d: "M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z",
				"clip-rule": "evenodd"
			})], -1))])]),
			createBaseVNode("div", _hoisted_9$3, [createBaseVNode("div", _hoisted_10$3, [createBaseVNode("div", null, [_cache[16] || (_cache[16] = createBaseVNode("p", { class: "text-emerald-100 text-sm font-medium" }, "Avg Utilization", -1)), createBaseVNode("p", _hoisted_11$2, toDisplayString($options.avgUtilization.toFixed(0)) + "%", 1)]), _cache[17] || (_cache[17] = createBaseVNode("svg", {
				class: "w-12 h-12 text-emerald-200",
				fill: "currentColor",
				viewBox: "0 0 20 20"
			}, [createBaseVNode("path", {
				"fill-rule": "evenodd",
				d: "M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z",
				"clip-rule": "evenodd"
			})], -1))])]),
			createBaseVNode("div", _hoisted_12$2, [createBaseVNode("div", _hoisted_13$2, [createBaseVNode("div", null, [_cache[18] || (_cache[18] = createBaseVNode("p", { class: "text-amber-100 text-sm font-medium" }, "Active Departments", -1)), createBaseVNode("p", _hoisted_14$2, toDisplayString($options.activeCount), 1)]), _cache[19] || (_cache[19] = createBaseVNode("svg", {
				class: "w-12 h-12 text-amber-200",
				fill: "currentColor",
				viewBox: "0 0 20 20"
			}, [createBaseVNode("path", { d: "M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" })], -1))])])
		]),
		createBaseVNode("div", _hoisted_15$2, [createBaseVNode("div", _hoisted_16$2, [_cache[21] || (_cache[21] = createBaseVNode("h2", { class: "text-xl font-bold text-slate-900 dark:text-white" }, "Department Budgets", -1)), createBaseVNode("button", {
			onClick: _cache[0] || (_cache[0] = (...args) => $options.openAddModal && $options.openAddModal(...args)),
			class: "px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
		}, [..._cache[20] || (_cache[20] = [createBaseVNode("svg", {
			class: "w-4 h-4",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M12 4v16m8-8H4"
		})], -1), createTextVNode(" Add Department ", -1)])])]), createBaseVNode("div", _hoisted_17$2, [createBaseVNode("table", _hoisted_18$2, [_cache[24] || (_cache[24] = createBaseVNode("thead", { class: "bg-slate-50 dark:bg-slate-900" }, [createBaseVNode("tr", null, [
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Department"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Manager"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Budget"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Spent"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Remaining"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Utilization"),
			createBaseVNode("th", { class: "px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Status"),
			createBaseVNode("th", { class: "px-6 py-3 text-right text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider" }, "Actions")
		])], -1)), createBaseVNode("tbody", _hoisted_19$1, [(openBlock(true), createElementBlock(Fragment, null, renderList($props.data, (dept) => {
			return openBlock(), createElementBlock("tr", {
				key: dept.id,
				class: "hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors"
			}, [
				createBaseVNode("td", _hoisted_20$1, [createBaseVNode("div", _hoisted_21$1, toDisplayString(dept.name), 1), createBaseVNode("div", _hoisted_22$1, toDisplayString(dept.code), 1)]),
				createBaseVNode("td", _hoisted_23$1, [createBaseVNode("div", _hoisted_24$1, toDisplayString(dept.manager_name || "N/A"), 1)]),
				createBaseVNode("td", _hoisted_25$1, [createBaseVNode("div", _hoisted_26$1, "KES " + toDisplayString($options.formatNumber(dept.budget)), 1)]),
				createBaseVNode("td", _hoisted_27$1, [createBaseVNode("div", _hoisted_28$1, "KES " + toDisplayString($options.formatNumber(dept.spent)), 1)]),
				createBaseVNode("td", _hoisted_29$1, [createBaseVNode("div", { class: normalizeClass(["text-sm", dept.remaining >= 0 ? "text-emerald-600 dark:text-emerald-400" : "text-red-600 dark:text-red-400"]) }, " KES " + toDisplayString($options.formatNumber(dept.remaining)), 3)]),
				createBaseVNode("td", _hoisted_30$1, [createBaseVNode("div", _hoisted_31$1, [createBaseVNode("div", _hoisted_32$1, [createBaseVNode("div", {
					class: normalizeClass(["h-2 rounded-full transition-all", $options.getUtilizationColor(dept.utilization)]),
					style: normalizeStyle({ width: Math.min(dept.utilization, 100) + "%" })
				}, null, 6)]), createBaseVNode("span", _hoisted_33$1, toDisplayString(dept.utilization.toFixed(0)) + "%", 1)])]),
				createBaseVNode("td", _hoisted_34$1, [dept.is_active ? (openBlock(), createElementBlock("span", _hoisted_35$1, " Active ")) : (openBlock(), createElementBlock("span", _hoisted_36$1, " Inactive "))]),
				createBaseVNode("td", _hoisted_37$1, [createBaseVNode("div", _hoisted_38$1, [createBaseVNode("button", {
					onClick: ($event) => $options.openEditModal(dept),
					class: "p-2 hover:bg-blue-100 dark:hover:bg-blue-600 rounded transition-colors",
					title: "Edit"
				}, [..._cache[22] || (_cache[22] = [createBaseVNode("svg", {
					class: "w-4 h-4 text-blue-600 dark:text-blue-400",
					fill: "none",
					stroke: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", {
					"stroke-linecap": "round",
					"stroke-linejoin": "round",
					"stroke-width": "2",
					d: "M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
				})], -1)])], 8, _hoisted_39$1), createBaseVNode("button", {
					onClick: ($event) => $options.openDeleteModal(dept),
					class: "p-2 hover:bg-red-100 dark:hover:bg-red-600 rounded transition-colors",
					title: "Delete"
				}, [..._cache[23] || (_cache[23] = [createBaseVNode("svg", {
					class: "w-4 h-4 text-red-600 dark:text-red-400",
					fill: "none",
					stroke: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", {
					"stroke-linecap": "round",
					"stroke-linejoin": "round",
					"stroke-width": "2",
					d: "M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
				})], -1)])], 8, _hoisted_40$1)])])
			]);
		}), 128))])])])]),
		$data.showFormModal ? (openBlock(), createElementBlock("div", {
			key: 0,
			class: "fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4",
			onClick: _cache[8] || (_cache[8] = withModifiers((...args) => $options.closeFormModal && $options.closeFormModal(...args), ["self"]))
		}, [createBaseVNode("div", _hoisted_41$1, [
			createBaseVNode("div", _hoisted_42$1, [createBaseVNode("h2", _hoisted_43$1, toDisplayString($data.selectedDepartment ? "Edit Department" : "Add Department"), 1), createBaseVNode("button", {
				onClick: _cache[1] || (_cache[1] = (...args) => $options.closeFormModal && $options.closeFormModal(...args)),
				class: "p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
			}, [..._cache[25] || (_cache[25] = [createBaseVNode("svg", {
				class: "w-5 h-5",
				fill: "none",
				stroke: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M6 18L18 6M6 6l12 12"
			})], -1)])])]),
			createBaseVNode("div", _hoisted_44$1, [
				createBaseVNode("div", _hoisted_45$1, [createBaseVNode("div", null, [_cache[26] || (_cache[26] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2" }, "Name *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => $data.formData.name = $event),
					type: "text",
					required: "",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $data.formData.name]])]), createBaseVNode("div", null, [_cache[27] || (_cache[27] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2" }, "Code *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => $data.formData.code = $event),
					type: "text",
					required: "",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $data.formData.code]])])]),
				createBaseVNode("div", null, [_cache[28] || (_cache[28] = createBaseVNode("label", { class: "block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2" }, "Budget (KES) *", -1)), withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[4] || (_cache[4] = ($event) => $data.formData.budget = $event),
					type: "number",
					step: "0.01",
					required: "",
					class: "w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
				}, null, 512), [[vModelText, $data.formData.budget]])]),
				createBaseVNode("div", null, [createBaseVNode("label", _hoisted_46$1, [withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[5] || (_cache[5] = ($event) => $data.formData.is_active = $event),
					type: "checkbox",
					class: "w-4 h-4 text-blue-600 border-slate-300 dark:border-slate-600 rounded"
				}, null, 512), [[vModelCheckbox, $data.formData.is_active]]), _cache[29] || (_cache[29] = createBaseVNode("span", { class: "text-sm text-slate-700 dark:text-slate-300" }, "Active Department", -1))])])
			]),
			createBaseVNode("div", _hoisted_47$1, [createBaseVNode("button", {
				onClick: _cache[6] || (_cache[6] = (...args) => $options.closeFormModal && $options.closeFormModal(...args)),
				class: "px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg"
			}, "Cancel"), createBaseVNode("button", {
				onClick: _cache[7] || (_cache[7] = (...args) => $options.saveDepartment && $options.saveDepartment(...args)),
				disabled: $data.saveLoading,
				class: normalizeClass(["px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg", { "opacity-50": $data.saveLoading }])
			}, toDisplayString($data.saveLoading ? "Saving..." : "Save"), 11, _hoisted_48)])
		])])) : createCommentVNode("", true),
		$data.showDeleteModal ? (openBlock(), createElementBlock("div", {
			key: 1,
			class: "fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4",
			onClick: _cache[11] || (_cache[11] = withModifiers((...args) => $options.closeDeleteModal && $options.closeDeleteModal(...args), ["self"]))
		}, [createBaseVNode("div", _hoisted_49, [createBaseVNode("div", _hoisted_50, [createBaseVNode("div", _hoisted_51, [_cache[31] || (_cache[31] = createBaseVNode("div", { class: "w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center" }, [createBaseVNode("svg", {
			class: "w-6 h-6 text-red-600 dark:text-red-400",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
		})])], -1)), createBaseVNode("div", null, [_cache[30] || (_cache[30] = createBaseVNode("h3", { class: "text-lg font-semibold text-slate-900 dark:text-white" }, "Delete Department", -1)), createBaseVNode("p", _hoisted_52, "Are you sure you want to delete \"" + toDisplayString($data.departmentToDelete?.name) + "\"?", 1)])])]), createBaseVNode("div", _hoisted_53, [createBaseVNode("button", {
			onClick: _cache[9] || (_cache[9] = (...args) => $options.closeDeleteModal && $options.closeDeleteModal(...args)),
			class: "px-4 py-2 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-900 dark:text-white rounded-lg"
		}, "Cancel"), createBaseVNode("button", {
			onClick: _cache[10] || (_cache[10] = (...args) => $options.confirmDelete && $options.confirmDelete(...args)),
			disabled: $data.deleteLoading,
			class: normalizeClass(["px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg", { "opacity-50": $data.deleteLoading }])
		}, toDisplayString($data.deleteLoading ? "Deleting..." : "Delete"), 11, _hoisted_54)])])])) : createCommentVNode("", true)
	]);
}
var _sfc_main$2 = {
	name: "Finance",
	components: {
		FinancialAnalytics: FinancialAnalytics_default,
		RevenueStreams: RevenueStreams_default,
		Expenses: Expenses_default,
		Investments: Investments_default,
		Departments: /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$3, [["render", _sfc_render$3]])
	},
	data() {
		return {
			activeTab: "analytics",
			tabs: [
				{
					id: "analytics",
					name: "Analytics"
				},
				{
					id: "revenue-streams",
					name: "Revenue Streams"
				},
				{
					id: "expenses",
					name: "Expenses"
				},
				{
					id: "investments",
					name: "Investments"
				},
				{
					id: "departments",
					name: "Departments"
				}
			],
			loading: false,
			metrics: {
				mrr: 0,
				arr: 0,
				arpu: 0,
				ltv: 0,
				growth_rate: 0
			},
			packagePerformance: [],
			revenueStreams: [],
			expenses: [],
			investments: [],
			departments: []
		};
	},
	methods: {
		async fetchMetrics() {
			try {
				this.loading = true;
				const response = await fetch("/api/finance/api/metrics/", { headers: { "Authorization": `Bearer ${localStorage.getItem("access_token")}` } });
				if (!response.ok) throw new Error("Failed to fetch");
				const data = await response.json();
				this.metrics = {
					mrr: data.mrr || 0,
					arr: data.arr || 0,
					arpu: data.arpu || 0,
					ltv: data.ltv || 0,
					growth_rate: 0
				};
			} catch (error) {
				console.error("Error fetching metrics:", error);
			} finally {
				this.loading = false;
			}
		},
		async fetchPackagePerformance() {
			try {
				const response = await fetch("/api/finance/api/package-performance/", { headers: { "Authorization": `Bearer ${localStorage.getItem("access_token")}` } });
				if (!response.ok) throw new Error("Failed to fetch");
				this.packagePerformance = (await response.json()).map((pkg) => ({
					name: pkg.package_name,
					sales: pkg.sales,
					revenue: pkg.revenue,
					profit: pkg.revenue * .7,
					margin: 70
				}));
			} catch (error) {
				console.error("Error fetching package performance:", error);
			}
		},
		async fetchRevenueStreams() {
			try {
				const response = await fetch("/api/finance/api/revenue-streams/", { headers: { "Authorization": `Bearer ${localStorage.getItem("access_token")}` } });
				if (!response.ok) throw new Error("Failed to fetch");
				this.revenueStreams = await response.json();
			} catch (error) {
				console.error("Error fetching revenue streams:", error);
				this.revenueStreams = [];
			}
		},
		async fetchExpenses() {
			try {
				const response = await fetch("/api/finance/api/expenses/", { headers: { "Authorization": `Bearer ${localStorage.getItem("access_token")}` } });
				if (!response.ok) throw new Error("Failed to fetch");
				this.expenses = await response.json();
			} catch (error) {
				console.error("Error fetching expenses:", error);
				this.expenses = [];
			}
		},
		async fetchInvestments() {
			try {
				const response = await fetch("/api/finance/api/investments/", { headers: { "Authorization": `Bearer ${localStorage.getItem("access_token")}` } });
				if (!response.ok) throw new Error("Failed to fetch");
				this.investments = await response.json();
			} catch (error) {
				console.error("Error fetching investments:", error);
				this.investments = [];
			}
		},
		async fetchDepartments() {
			try {
				const response = await fetch("/api/finance/api/departments/", { headers: { "Authorization": `Bearer ${localStorage.getItem("access_token")}` } });
				if (!response.ok) throw new Error("Failed to fetch");
				this.departments = await response.json();
			} catch (error) {
				console.error("Error fetching departments:", error);
				this.departments = [];
			}
		},
		refreshData() {
			this.fetchMetrics();
			this.fetchPackagePerformance();
			this.fetchRevenueStreams();
			this.fetchExpenses();
			this.fetchInvestments();
			this.fetchDepartments();
		}
	},
	mounted() {
		this.refreshData();
	}
};
var _hoisted_1$2 = { class: "p-6 space-y-6" };
var _hoisted_2$2 = { class: "flex justify-between items-center" };
var _hoisted_3$2 = { class: "border-b border-slate-200 dark:border-slate-700" };
var _hoisted_4$2 = { class: "-mb-px flex space-x-8" };
var _hoisted_5$2 = ["onClick"];
var _hoisted_6$2 = { key: 0 };
var _hoisted_7$2 = { key: 1 };
var _hoisted_8$2 = { key: 2 };
var _hoisted_9$2 = { key: 3 };
var _hoisted_10$2 = { key: 4 };
function _sfc_render$2(_ctx, _cache, $props, $setup, $data, $options) {
	const _component_FinancialAnalytics = resolveComponent("FinancialAnalytics");
	const _component_RevenueStreams = resolveComponent("RevenueStreams");
	const _component_Expenses = resolveComponent("Expenses");
	const _component_Investments = resolveComponent("Investments");
	const _component_Departments = resolveComponent("Departments");
	return openBlock(), createElementBlock("div", _hoisted_1$2, [
		createBaseVNode("div", _hoisted_2$2, [_cache[2] || (_cache[2] = createBaseVNode("div", null, [createBaseVNode("h1", { class: "text-3xl font-bold text-slate-900 dark:text-white" }, "Finance Management"), createBaseVNode("p", { class: "text-slate-600 dark:text-slate-400 mt-1" }, "Manage revenue streams, expenses, investments, and financial reports")], -1)), createBaseVNode("button", {
			onClick: _cache[0] || (_cache[0] = (...args) => $options.refreshData && $options.refreshData(...args)),
			class: "px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
		}, [..._cache[1] || (_cache[1] = [createBaseVNode("svg", {
			class: "w-5 h-5",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
		})], -1), createTextVNode(" Refresh ", -1)])])]),
		createBaseVNode("div", _hoisted_3$2, [createBaseVNode("nav", _hoisted_4$2, [(openBlock(true), createElementBlock(Fragment, null, renderList($data.tabs, (tab) => {
			return openBlock(), createElementBlock("button", {
				key: tab.id,
				onClick: ($event) => $data.activeTab = tab.id,
				class: normalizeClass(["py-4 px-1 border-b-2 font-medium text-sm transition-colors", $data.activeTab === tab.id ? "border-blue-500 text-blue-600 dark:text-blue-400" : "border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300 dark:text-slate-400 dark:hover:text-slate-300"])
			}, toDisplayString(tab.name), 11, _hoisted_5$2);
		}), 128))])]),
		createBaseVNode("div", null, [
			$data.activeTab === "analytics" ? (openBlock(), createElementBlock("div", _hoisted_6$2, [createVNode(_component_FinancialAnalytics, {
				metrics: $data.metrics,
				packages: $data.packagePerformance,
				loading: $data.loading
			}, null, 8, [
				"metrics",
				"packages",
				"loading"
			])])) : createCommentVNode("", true),
			$data.activeTab === "revenue-streams" ? (openBlock(), createElementBlock("div", _hoisted_7$2, [createVNode(_component_RevenueStreams, {
				data: $data.revenueStreams,
				onRefresh: $options.fetchRevenueStreams
			}, null, 8, ["data", "onRefresh"])])) : createCommentVNode("", true),
			$data.activeTab === "expenses" ? (openBlock(), createElementBlock("div", _hoisted_8$2, [createVNode(_component_Expenses, {
				data: $data.expenses,
				onRefresh: $options.fetchExpenses
			}, null, 8, ["data", "onRefresh"])])) : createCommentVNode("", true),
			$data.activeTab === "investments" ? (openBlock(), createElementBlock("div", _hoisted_9$2, [createVNode(_component_Investments, {
				data: $data.investments,
				onRefresh: $options.fetchInvestments
			}, null, 8, ["data", "onRefresh"])])) : createCommentVNode("", true),
			$data.activeTab === "departments" ? (openBlock(), createElementBlock("div", _hoisted_10$2, [createVNode(_component_Departments, {
				data: $data.departments,
				onRefresh: $options.fetchDepartments
			}, null, 8, ["data", "onRefresh"])])) : createCommentVNode("", true)
		])
	]);
}
var Finance_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$2, [["render", _sfc_render$2]]);
var _sfc_main$1 = {
	name: "Auth",
	components: {
		ShieldCheckIcon: render,
		UserIcon: render$1,
		LockClosedIcon: render$2,
		EyeIcon: render$3,
		EyeSlashIcon: render$4,
		ArrowRightIcon: render$5,
		ExclamationCircleIcon: render$6,
		ExclamationTriangleIcon: render$7,
		XMarkIcon: render$8
	},
	emits: ["login-success"],
	setup(props, { emit }) {
		const loading = ref(false);
		const showPassword = ref(false);
		const showError = ref(false);
		const errorMessage = ref("");
		const loginForm = reactive({
			username: "",
			password: ""
		});
		const formErrors = reactive({
			username: "",
			password: ""
		});
		const clearError = (field) => {
			if (formErrors[field]) formErrors[field] = "";
		};
		const validateForm = () => {
			let valid = true;
			formErrors.username = "";
			formErrors.password = "";
			if (!loginForm.username.trim()) {
				formErrors.username = "Admin username is required";
				valid = false;
			}
			if (!loginForm.password) {
				formErrors.password = "Password is required";
				valid = false;
			}
			return valid;
		};
		const handleLogin = async () => {
			if (!validateForm()) return;
			loading.value = true;
			showError.value = false;
			try {
				console.log("🚀 Starting JWT authentication...");
				const PRIMARY_URL$1 = "https://srv.teralinkxwaves.uk";
				const FALLBACK_URL$1 = "https://accounts.teralinkxwaves.uk";
				let response;
				let usedFallback = false;
				try {
					console.log("📡 Trying primary:", PRIMARY_URL$1);
					response = await fetch(`${PRIMARY_URL$1}/suapi/auth/login/`, {
						method: "POST",
						headers: { "Content-Type": "application/json" },
						body: JSON.stringify({
							username: loginForm.username,
							password: loginForm.password
						}),
						signal: AbortSignal.timeout(5e3)
					});
				} catch (primaryError) {
					console.warn("⚠️ Primary failed, trying fallback:", FALLBACK_URL$1);
					usedFallback = true;
					response = await fetch(`${FALLBACK_URL$1}/suapi/auth/login/`, {
						method: "POST",
						headers: { "Content-Type": "application/json" },
						body: JSON.stringify({
							username: loginForm.username,
							password: loginForm.password
						})
					});
				}
				console.log(`📨 Login response status: ${response.status} (via ${usedFallback ? "fallback" : "primary"})`);
				const data = await response.json();
				console.log("📊 Login response data:", data);
				if (response.ok && data.success) {
					console.log("✅ JWT Login successful");
					const { tokens, user } = data;
					if (tokens && tokens.access && tokens.refresh) {
						emit("login-success", {
							access: tokens.access,
							refresh: tokens.refresh,
							user
						});
						console.log("🎉 Login successful, tokens emitted to App.vue");
					} else throw new Error("No tokens received from server");
				} else throw new Error(data.message || "Authentication failed");
			} catch (error) {
				console.error("❌ Authentication error:", error);
				let userMessage = error.message;
				if (error.message.includes("Network") || error.message.includes("Fetch")) userMessage = "Network error. Please check your connection and try again.";
				showError.value = true;
				errorMessage.value = userMessage;
				setTimeout(() => {
					showError.value = false;
				}, 5e3);
			} finally {
				loading.value = false;
			}
		};
		return {
			loading,
			showPassword,
			showError,
			errorMessage,
			loginForm,
			formErrors,
			clearError,
			handleLogin
		};
	}
};
var _hoisted_1$1 = { class: "min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center p-4" };
var _hoisted_2$1 = { class: "relative w-full max-w-md" };
var _hoisted_3$1 = { class: "bg-white/80 backdrop-blur-lg rounded-3xl shadow-2xl border border-white/20 p-8" };
var _hoisted_4$1 = { class: "text-center mb-8" };
var _hoisted_5$1 = { class: "w-20 h-20 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg" };
var _hoisted_6$1 = { class: "block text-sm font-medium text-slate-700 mb-2 flex items-center" };
var _hoisted_7$1 = { class: "relative" };
var _hoisted_8$1 = {
	key: 0,
	class: "text-rose-600 text-xs mt-2 flex items-center"
};
var _hoisted_9$1 = { class: "block text-sm font-medium text-slate-700 mb-2 flex items-center" };
var _hoisted_10$1 = { class: "relative" };
var _hoisted_11$1 = ["type"];
var _hoisted_12$1 = {
	key: 0,
	class: "text-rose-600 text-xs mt-2 flex items-center"
};
var _hoisted_13$1 = ["disabled"];
var _hoisted_14$1 = {
	key: 0,
	class: "flex items-center space-x-2"
};
var _hoisted_15$1 = {
	key: 1,
	class: "flex items-center space-x-2"
};
var _hoisted_16$1 = {
	key: 0,
	class: "fixed top-4 right-4 z-50"
};
var _hoisted_17$1 = { class: "bg-rose-500 text-white px-6 py-4 rounded-xl shadow-lg flex items-center space-x-3 animate-fade-in" };
var _hoisted_18$1 = { class: "text-sm opacity-90" };
function _sfc_render$1(_ctx, _cache, $props, $setup, $data, $options) {
	const _component_ShieldCheckIcon = resolveComponent("ShieldCheckIcon");
	const _component_UserIcon = resolveComponent("UserIcon");
	const _component_ExclamationCircleIcon = resolveComponent("ExclamationCircleIcon");
	const _component_LockClosedIcon = resolveComponent("LockClosedIcon");
	const _component_EyeIcon = resolveComponent("EyeIcon");
	const _component_EyeSlashIcon = resolveComponent("EyeSlashIcon");
	const _component_ArrowRightIcon = resolveComponent("ArrowRightIcon");
	const _component_ExclamationTriangleIcon = resolveComponent("ExclamationTriangleIcon");
	const _component_XMarkIcon = resolveComponent("XMarkIcon");
	return openBlock(), createElementBlock("div", _hoisted_1$1, [
		_cache[14] || (_cache[14] = createBaseVNode("div", { class: "absolute inset-0 overflow-hidden" }, [
			createBaseVNode("div", { class: "absolute -top-40 -right-40 w-80 h-80 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob" }),
			createBaseVNode("div", { class: "absolute -bottom-40 -left-40 w-80 h-80 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000" }),
			createBaseVNode("div", { class: "absolute top-40 left-40 w-80 h-80 bg-indigo-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000" })
		], -1)),
		createBaseVNode("div", _hoisted_2$1, [createBaseVNode("div", _hoisted_3$1, [createBaseVNode("div", _hoisted_4$1, [
			createBaseVNode("div", _hoisted_5$1, [createVNode(_component_ShieldCheckIcon, { class: "w-10 h-10 text-white" })]),
			_cache[7] || (_cache[7] = createBaseVNode("h1", { class: "text-3xl font-bold bg-gradient-to-r from-slate-800 to-blue-600 bg-clip-text text-transparent mb-2" }, " Admin Access ", -1)),
			_cache[8] || (_cache[8] = createBaseVNode("p", { class: "text-slate-600 font-light" }, "Authorized personnel only", -1))
		]), createBaseVNode("form", {
			onSubmit: _cache[5] || (_cache[5] = withModifiers((...args) => $setup.handleLogin && $setup.handleLogin(...args), ["prevent"])),
			class: "space-y-6"
		}, [
			createBaseVNode("div", null, [
				createBaseVNode("label", _hoisted_6$1, [createVNode(_component_UserIcon, { class: "w-4 h-4 mr-2" }), _cache[9] || (_cache[9] = createTextVNode(" Admin Username ", -1))]),
				createBaseVNode("div", _hoisted_7$1, [withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => $setup.loginForm.username = $event),
					type: "text",
					required: "",
					placeholder: "Enter admin username",
					class: normalizeClass(["w-full px-4 py-3 pl-11 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300 bg-white/50 backdrop-blur-sm", $setup.formErrors.username ? "border-rose-500" : "border-slate-300"]),
					onInput: _cache[1] || (_cache[1] = ($event) => $setup.clearError("username"))
				}, null, 34), [[vModelText, $setup.loginForm.username]]), createVNode(_component_UserIcon, { class: "w-5 h-5 text-slate-400 absolute left-3 top-1/2 transform -translate-y-1/2" })]),
				$setup.formErrors.username ? (openBlock(), createElementBlock("p", _hoisted_8$1, [createVNode(_component_ExclamationCircleIcon, { class: "w-4 h-4 mr-1" }), createTextVNode(" " + toDisplayString($setup.formErrors.username), 1)])) : createCommentVNode("", true)
			]),
			createBaseVNode("div", null, [
				createBaseVNode("label", _hoisted_9$1, [createVNode(_component_LockClosedIcon, { class: "w-4 h-4 mr-2" }), _cache[10] || (_cache[10] = createTextVNode(" Password ", -1))]),
				createBaseVNode("div", _hoisted_10$1, [
					withDirectives(createBaseVNode("input", {
						"onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => $setup.loginForm.password = $event),
						type: $setup.showPassword ? "text" : "password",
						required: "",
						placeholder: "Enter your password",
						class: normalizeClass(["w-full px-4 py-3 pl-11 pr-11 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300 bg-white/50 backdrop-blur-sm", $setup.formErrors.password ? "border-rose-500" : "border-slate-300"]),
						onInput: _cache[3] || (_cache[3] = ($event) => $setup.clearError("password"))
					}, null, 42, _hoisted_11$1), [[vModelDynamic, $setup.loginForm.password]]),
					createVNode(_component_LockClosedIcon, { class: "w-5 h-5 text-slate-400 absolute left-3 top-1/2 transform -translate-y-1/2" }),
					createBaseVNode("button", {
						type: "button",
						onClick: _cache[4] || (_cache[4] = ($event) => $setup.showPassword = !$setup.showPassword),
						class: "absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors duration-200"
					}, [$setup.showPassword ? (openBlock(), createBlock(_component_EyeIcon, {
						key: 0,
						class: "w-5 h-5"
					})) : (openBlock(), createBlock(_component_EyeSlashIcon, {
						key: 1,
						class: "w-5 h-5"
					}))])
				]),
				$setup.formErrors.password ? (openBlock(), createElementBlock("p", _hoisted_12$1, [createVNode(_component_ExclamationCircleIcon, { class: "w-4 h-4 mr-1" }), createTextVNode(" " + toDisplayString($setup.formErrors.password), 1)])) : createCommentVNode("", true)
			]),
			createBaseVNode("button", {
				type: "submit",
				disabled: $setup.loading,
				class: normalizeClass(["w-full py-4 px-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transform transition-all duration-300 flex items-center justify-center space-x-2", $setup.loading ? "opacity-50 cursor-not-allowed" : "hover:scale-105"])
			}, [$setup.loading ? (openBlock(), createElementBlock("div", _hoisted_14$1, [..._cache[11] || (_cache[11] = [createBaseVNode("div", { class: "w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" }, null, -1), createBaseVNode("span", null, "Authenticating...", -1)])])) : (openBlock(), createElementBlock("div", _hoisted_15$1, [createVNode(_component_ArrowRightIcon, { class: "w-5 h-5" }), _cache[12] || (_cache[12] = createBaseVNode("span", null, "Access Dashboard", -1))]))], 10, _hoisted_13$1)
		], 32)])]),
		$setup.showError ? (openBlock(), createElementBlock("div", _hoisted_16$1, [createBaseVNode("div", _hoisted_17$1, [
			createVNode(_component_ExclamationTriangleIcon, { class: "w-5 h-5" }),
			createBaseVNode("div", null, [_cache[13] || (_cache[13] = createBaseVNode("p", { class: "font-medium" }, "Authentication Failed", -1)), createBaseVNode("p", _hoisted_18$1, toDisplayString($setup.errorMessage), 1)]),
			createBaseVNode("button", {
				onClick: _cache[6] || (_cache[6] = ($event) => $setup.showError = false),
				class: "text-white/80 hover:text-white"
			}, [createVNode(_component_XMarkIcon, { class: "w-5 h-5" })])
		])])) : createCommentVNode("", true)
	]);
}
var Auth_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main$1, [["render", _sfc_render$1], ["__scopeId", "data-v-edb01d16"]]);
axios_default.defaults.baseURL = "https://srv.teralinkxwaves.uk";
axios_default.defaults.headers.common["Content-Type"] = "application/json";
var _sfc_main = {
	name: "App",
	setup() {
		const { initTheme } = useTheme();
		initTheme();
		return {};
	},
	components: {
		Sidebar: Sidebar_default,
		RealTimeNotifications: RealTimeNotifications_default,
		Dashboard: Dashboard_default,
		Analytics: Analytics_default,
		Clients: Clients_default,
		Users: Users_default,
		Devices: Devices_default,
		Sessions: Sessions_default,
		Packages: Packages_default,
		Vouchers: Vouchers_default,
		Coupons: Coupons_default,
		Promotions: Promotions_default,
		PointTransactions: PointTransactions_default,
		Locations: Locations_default,
		Transactions: Transactions_default,
		Refunds: Refunds_default,
		Finance: Finance_default,
		Auth: Auth_default
	},
	data() {
		return {
			activeComponent: "Dashboard",
			isMobileSidebarOpen: false,
			isSidebarCollapsed: false,
			showToast: false,
			toastMessage: "",
			isAuthenticated: false,
			authChecked: false,
			user: null,
			refreshTokenInterval: null,
			axiosInterceptor: null,
			globalSearch: "",
			showSearchResults: false,
			showNotifications: false,
			showUserMenu: false,
			notifications: [
				{
					id: 1,
					icon: "🔔",
					title: "New User Registration",
					message: "5 new users registered today",
					time: "5 min ago",
					read: false
				},
				{
					id: 2,
					icon: "💳",
					title: "Payment Received",
					message: "Payment of $150 received",
					time: "1 hour ago",
					read: false
				},
				{
					id: 3,
					icon: "⚠️",
					title: "System Alert",
					message: "High server load detected",
					time: "2 hours ago",
					read: true
				}
			],
			sidebarStats: {
				activeUsers: 0,
				activeSessions: 0,
				activeDevices: 0,
				pendingRefunds: 0
			}
		};
	},
	computed: {
		unreadNotifications() {
			return this.notifications.filter((n) => !n.read).length;
		},
		searchResults() {
			if (!this.globalSearch) return [];
			const query = this.globalSearch.toLowerCase();
			const results = [];
			[
				{
					id: "dashboard",
					icon: "📊",
					title: "Dashboard",
					subtitle: "Overview and analytics",
					component: "Dashboard"
				},
				{
					id: "clients",
					icon: "👥",
					title: "Clients",
					subtitle: "Manage client profiles",
					component: "Clients"
				},
				{
					id: "users",
					icon: "🔐",
					title: "Users",
					subtitle: "User management",
					component: "Users"
				},
				{
					id: "devices",
					icon: "📱",
					title: "Devices",
					subtitle: "Connected devices",
					component: "Devices"
				},
				{
					id: "sessions",
					icon: "🔌",
					title: "Sessions",
					subtitle: "Active sessions",
					component: "Sessions"
				},
				{
					id: "packages",
					icon: "📦",
					title: "Packages",
					subtitle: "Data packages",
					component: "Packages"
				},
				{
					id: "vouchers",
					icon: "🎫",
					title: "Vouchers",
					subtitle: "Voucher management",
					component: "Vouchers"
				},
				{
					id: "coupons",
					icon: "🎟️",
					title: "Coupons",
					subtitle: "Discount coupons",
					component: "Coupons"
				},
				{
					id: "promotions",
					icon: "🎁",
					title: "Promotions",
					subtitle: "Marketing promotions",
					component: "Promotions"
				},
				{
					id: "points",
					icon: "🏆",
					title: "Points",
					subtitle: "Reward points",
					component: "PointTransactions"
				},
				{
					id: "locations",
					icon: "📍",
					title: "Locations",
					subtitle: "Network locations",
					component: "Locations"
				},
				{
					id: "transactions",
					icon: "💳",
					title: "Transactions",
					subtitle: "Payment transactions",
					component: "Transactions"
				},
				{
					id: "refunds",
					icon: "🔄",
					title: "Refunds",
					subtitle: "Refund requests",
					component: "Refunds"
				}
			].forEach((page) => {
				if (page.title.toLowerCase().includes(query) || page.subtitle.toLowerCase().includes(query)) results.push(page);
			});
			return results.slice(0, 5);
		}
	},
	methods: {
		setActiveComponent(componentName) {
			this.activeComponent = componentName;
			if (window.innerWidth < 1024) this.isMobileSidebarOpen = false;
			this.showNotifications = false;
			this.showUserMenu = false;
			this.showSearchResults = false;
		},
		getUserInitials() {
			if (!this.user?.username) return "AD";
			const parts = this.user.username.split(" ");
			if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
			return this.user.username.substring(0, 2).toUpperCase();
		},
		toggleNotifications() {
			this.showNotifications = !this.showNotifications;
			this.showUserMenu = false;
			this.showSearchResults = false;
		},
		toggleUserMenu() {
			this.showUserMenu = !this.showUserMenu;
			this.showNotifications = false;
			this.showSearchResults = false;
		},
		hideSearchResults() {
			setTimeout(() => {
				this.showSearchResults = false;
			}, 200);
		},
		navigateToResult(result) {
			this.setActiveComponent(result.component);
			this.globalSearch = "";
			this.showSearchResults = false;
		},
		markAllAsRead() {
			this.notifications.forEach((n) => n.read = true);
		},
		handleNotificationClick(notif) {
			notif.read = true;
			this.showNotifications = false;
		},
		async fetchSidebarStats() {
			try {
				const [usersRes, sessionsRes, devicesRes] = await Promise.all([
					axios_default.get("/suapi/users/stats/"),
					axios_default.get("/suapi/sessions/stats/"),
					axios_default.get("/suapi/devices/stats/")
				]);
				this.sidebarStats = {
					activeUsers: usersRes.data.active_users || 0,
					activeSessions: sessionsRes.data.active_sessions || 0,
					activeDevices: devicesRes.data.online_devices || 0,
					pendingRefunds: 0
				};
			} catch (error) {
				console.error("Error fetching sidebar stats:", error);
			}
		},
		refreshData() {
			if (this.$refs[this.activeComponent]?.refreshData) this.$refs[this.activeComponent].refreshData();
			this.showToastMessage("Data refreshed successfully!");
		},
		showToastMessage(message) {
			this.toastMessage = message;
			this.showToast = true;
			setTimeout(() => {
				this.showToast = false;
			}, 3e3);
		},
		toggleMobileSidebar() {
			this.isMobileSidebarOpen = !this.isMobileSidebarOpen;
			console.log("Mobile sidebar toggled:", this.isMobileSidebarOpen);
		},
		closeMobileSidebar() {
			this.isMobileSidebarOpen = false;
		},
		handleSidebarToggle(isCollapsed) {
			this.isSidebarCollapsed = isCollapsed;
		},
		setupAxiosInterceptor() {
			if (this.axiosInterceptor) axios_default.interceptors.response.eject(this.axiosInterceptor);
			this.axiosInterceptor = axios_default.interceptors.response.use((response) => response, async (error) => {
				const originalRequest = error.config;
				if (error.response?.status === 401 && !originalRequest._retry) {
					originalRequest._retry = true;
					try {
						console.log("🔄 Token expired, attempting refresh...");
						await this.refreshAccessToken();
						const newToken = localStorage.getItem("access_token");
						originalRequest.headers.Authorization = `Bearer ${newToken}`;
						return axios_default(originalRequest);
					} catch (refreshError) {
						console.error("❌ Token refresh failed:", refreshError);
						this.handleLogout();
						return Promise.reject(refreshError);
					}
				}
				return Promise.reject(error);
			});
		},
		setAuthHeader() {
			const token = localStorage.getItem("access_token");
			if (token) axios_default.defaults.headers.common["Authorization"] = `Bearer ${token}`;
			else delete axios_default.defaults.headers.common["Authorization"];
		},
		async checkAuthStatus() {
			const accessToken = localStorage.getItem("access_token");
			const refreshToken = localStorage.getItem("refresh_token");
			if (!accessToken || !refreshToken) {
				console.log("❌ No JWT tokens found");
				this.isAuthenticated = false;
				this.user = null;
				this.authChecked = true;
				return;
			}
			this.setAuthHeader();
			try {
				console.log("🔍 Verifying JWT token...");
				const response = await axios_default.get("/suapi/auth/verify/");
				if (response.data.authenticated) {
					console.log("✅ JWT token verified successfully");
					this.isAuthenticated = true;
					this.user = response.data.user;
					const storedUser = localStorage.getItem("user");
					if (storedUser) this.user = {
						...response.data.user,
						...JSON.parse(storedUser)
					};
				} else {
					console.log("❌ JWT token verification failed");
					this.isAuthenticated = false;
					this.user = null;
				}
			} catch (error) {
				console.error("❌ Auth check failed:", error);
				if (error.response?.status === 401) try {
					console.log("🔄 Access token expired, attempting refresh...");
					await this.refreshAccessToken();
					await this.checkAuthStatus();
					return;
				} catch (refreshError) {
					console.error("❌ Token refresh failed:", refreshError);
				}
				this.isAuthenticated = false;
				this.user = null;
			} finally {
				this.authChecked = true;
			}
		},
		async refreshAccessToken() {
			const refreshToken = localStorage.getItem("refresh_token");
			if (!refreshToken) throw new Error("No refresh token available");
			try {
				console.log("🔄 Refreshing access token...");
				const newAccessToken = (await axios_default.post("/suapi/token/refresh/", { refresh: refreshToken })).data.access;
				localStorage.setItem("access_token", newAccessToken);
				this.setAuthHeader();
				console.log("✅ Access token refreshed successfully");
				return newAccessToken;
			} catch (error) {
				console.error("❌ Token refresh failed:", error);
				this.clearTokens();
				throw error;
			}
		},
		handleLoginSuccess({ access, refresh, user }) {
			console.log("🎉 Login success received in App.vue");
			localStorage.setItem("access_token", access);
			localStorage.setItem("refresh_token", refresh);
			localStorage.setItem("user", JSON.stringify(user));
			this.setAuthHeader();
			this.isAuthenticated = true;
			this.user = user;
			this.authChecked = true;
			this.showToastMessage(`Welcome back, ${user.username}!`);
			console.log("✅ User authenticated and state updated");
		},
		clearTokens() {
			console.log("🧹 Clearing all tokens and user data");
			localStorage.removeItem("access_token");
			localStorage.removeItem("refresh_token");
			localStorage.removeItem("user");
			localStorage.removeItem("lastLogin");
			localStorage.removeItem("rememberMe");
			delete axios_default.defaults.headers.common["Authorization"];
		},
		async handleLogout() {
			try {
				const refreshToken = localStorage.getItem("refresh_token");
				if (refreshToken) await axios_default.post("/suapi/auth/logout/", { refresh_token: refreshToken });
			} catch (error) {
				console.error("Logout API error:", error);
			} finally {
				this.clearTokens();
				this.isAuthenticated = false;
				this.user = null;
				if (this.refreshTokenInterval) clearInterval(this.refreshTokenInterval);
				this.showToastMessage("Logged out successfully");
				console.log("✅ User logged out successfully");
			}
		},
		setupTokenRefresh() {
			this.refreshTokenInterval = setInterval(async () => {
				if (this.isAuthenticated) try {
					await this.refreshAccessToken();
					console.log("✅ Access token refreshed automatically");
				} catch (error) {
					console.error("❌ Automatic token refresh failed:", error);
					this.handleLogout();
				}
			}, 2700 * 1e3);
		},
		setupTokenExpirationCheck() {
			setInterval(() => {
				if (this.isAuthenticated) {
					const token = localStorage.getItem("access_token");
					if (token) try {
						const timeUntilExpiry = JSON.parse(atob(token.split(".")[1])).exp * 1e3 - Date.now();
						if (timeUntilExpiry < 300 * 1e3 && timeUntilExpiry > 0) {
							console.log("🔄 Token expiring soon, refreshing...");
							this.refreshAccessToken().catch((error) => {
								console.error("Preemptive token refresh failed:", error);
							});
						}
					} catch (error) {
						console.error("Error checking token expiration:", error);
					}
				}
			}, 60 * 1e3);
		}
	},
	provide() {
		return {
			closeMobileSidebar: () => {
				this.isMobileSidebarOpen = false;
			},
			openMobileSidebar: () => {
				this.isMobileSidebarOpen = true;
			}
		};
	},
	async mounted() {
		console.log("🚀 App.vue mounted - Initializing JWT authentication...");
		this.setupAxiosInterceptor();
		await this.checkAuthStatus();
		this.setupTokenRefresh();
		this.setupTokenExpirationCheck();
		if (this.isAuthenticated) {
			this.fetchSidebarStats();
			setInterval(() => {
				if (this.isAuthenticated) this.fetchSidebarStats();
			}, 3e4);
		}
		document.addEventListener("keydown", (e) => {
			if ((e.ctrlKey || e.metaKey) && e.key === "k") {
				e.preventDefault();
				document.querySelector("input[placeholder*=\"Search\"]")?.focus();
			}
			if (e.key === "Escape") {
				this.showNotifications = false;
				this.showUserMenu = false;
				this.showSearchResults = false;
			}
		});
		document.addEventListener("click", (e) => {
			if (!e.target.closest(".relative")) {
				this.showNotifications = false;
				this.showUserMenu = false;
			}
		});
		console.log("✅ App.vue initialization complete");
	},
	beforeUnmount() {
		if (this.refreshTokenInterval) clearInterval(this.refreshTokenInterval);
		if (this.axiosInterceptor) axios_default.interceptors.response.eject(this.axiosInterceptor);
	}
};
var _hoisted_1 = {
	id: "app",
	class: "min-h-screen bg-slate-50 dark:bg-slate-900 transition-colors duration-300"
};
var _hoisted_2 = { key: 0 };
var _hoisted_3 = {
	key: 0,
	class: "min-h-screen"
};
var _hoisted_4 = { class: "bg-white/60 dark:bg-slate-800/60 backdrop-blur-md border-b border-slate-200 dark:border-slate-700 sticky top-0 z-40 transition-colors duration-300" };
var _hoisted_5 = { class: "px-3 md:px-6 py-2 flex justify-between items-center gap-2" };
var _hoisted_6 = { class: "flex items-center space-x-4 flex-1" };
var _hoisted_7 = {
	key: 0,
	class: "w-6 h-6",
	fill: "none",
	stroke: "currentColor",
	viewBox: "0 0 24 24"
};
var _hoisted_8 = {
	key: 1,
	class: "w-6 h-6",
	fill: "none",
	stroke: "currentColor",
	viewBox: "0 0 24 24"
};
var _hoisted_9 = { class: "hidden lg:flex items-center space-x-2 text-sm" };
var _hoisted_10 = { class: "text-slate-900 dark:text-white font-medium" };
var _hoisted_11 = { class: "relative flex-1 max-w-md ml-2 md:ml-4" };
var _hoisted_12 = {
	key: 0,
	class: "absolute top-full mt-2 w-full bg-white dark:bg-slate-800 rounded-lg shadow-xl border border-slate-200 dark:border-slate-700 max-h-96 overflow-y-auto z-50"
};
var _hoisted_13 = {
	key: 0,
	class: "p-4 text-center text-slate-500 dark:text-slate-400 text-sm"
};
var _hoisted_14 = ["onMousedown"];
var _hoisted_15 = { class: "flex items-center space-x-3" };
var _hoisted_16 = { class: "text-lg" };
var _hoisted_17 = { class: "flex-1" };
var _hoisted_18 = { class: "text-sm font-medium text-slate-900 dark:text-white" };
var _hoisted_19 = { class: "text-xs text-slate-500 dark:text-slate-400" };
var _hoisted_20 = { class: "flex items-center space-x-2 md:space-x-3" };
var _hoisted_21 = { class: "relative" };
var _hoisted_22 = {
	key: 0,
	class: "absolute -top-1 -right-1 w-5 h-5 bg-rose-500 text-white text-xs rounded-full flex items-center justify-center font-bold shadow-lg"
};
var _hoisted_23 = {
	key: 0,
	class: "absolute right-0 mt-2 w-80 sm:w-96 bg-white dark:bg-slate-800 rounded-lg shadow-xl border border-slate-200 dark:border-slate-700 z-50 max-w-[calc(100vw-2rem)]"
};
var _hoisted_24 = { class: "p-3 md:p-4 border-b border-slate-200 dark:border-slate-700 flex justify-between items-center" };
var _hoisted_25 = { class: "max-h-96 overflow-y-auto" };
var _hoisted_26 = {
	key: 0,
	class: "p-4 text-center text-slate-500 dark:text-slate-400 text-sm"
};
var _hoisted_27 = ["onClick"];
var _hoisted_28 = { class: "flex items-start space-x-3" };
var _hoisted_29 = { class: "flex-1 min-w-0" };
var _hoisted_30 = { class: "text-sm font-medium text-slate-900 dark:text-white truncate" };
var _hoisted_31 = { class: "text-xs text-slate-500 dark:text-slate-400 mt-0.5" };
var _hoisted_32 = { class: "text-xs text-slate-400 dark:text-slate-500 mt-1" };
var _hoisted_33 = {
	key: 0,
	class: "w-2 h-2 bg-blue-500 rounded-full mt-2"
};
var _hoisted_34 = { class: "relative" };
var _hoisted_35 = { class: "hidden md:block text-left" };
var _hoisted_36 = { class: "text-sm font-medium text-slate-900 dark:text-white" };
var _hoisted_37 = { class: "text-xs text-slate-500 dark:text-slate-400" };
var _hoisted_38 = {
	key: 0,
	class: "absolute right-0 mt-2 w-56 bg-white dark:bg-slate-800 rounded-lg shadow-xl border border-slate-200 dark:border-slate-700 z-50"
};
var _hoisted_39 = { class: "p-3 md:p-4 border-b border-slate-200 dark:border-slate-700" };
var _hoisted_40 = { class: "text-sm font-semibold text-slate-900 dark:text-white truncate" };
var _hoisted_41 = { class: "text-xs text-slate-500 dark:text-slate-400 mt-0.5 truncate" };
var _hoisted_42 = { class: "border-t border-slate-200 dark:border-slate-700 py-2" };
var _hoisted_43 = { class: "p-6" };
var _hoisted_44 = {
	key: 0,
	class: "fixed top-4 right-4 bg-emerald-500 dark:bg-emerald-600 text-white px-5 py-3 rounded-lg shadow-lg z-50 animate-fade-in"
};
var _hoisted_45 = { class: "flex items-center space-x-2" };
var _hoisted_46 = { class: "text-sm font-medium" };
var _hoisted_47 = {
	key: 1,
	class: "min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-900"
};
function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
	const _component_Sidebar = resolveComponent("Sidebar");
	const _component_RealTimeNotifications = resolveComponent("RealTimeNotifications");
	const _component_Auth = resolveComponent("Auth");
	return openBlock(), createElementBlock("div", _hoisted_1, [$data.authChecked ? (openBlock(), createElementBlock("div", _hoisted_2, [$data.isAuthenticated ? (openBlock(), createElementBlock("div", _hoisted_3, [
		createVNode(_component_Sidebar, {
			onComponentSelected: $options.setActiveComponent,
			onRefreshData: $options.refreshData,
			"is-mobile-open": $data.isMobileSidebarOpen,
			onCloseMobile: $options.closeMobileSidebar,
			onSidebarToggle: $options.handleSidebarToggle,
			user: $data.user,
			stats: $data.sidebarStats
		}, null, 8, [
			"onComponentSelected",
			"onRefreshData",
			"is-mobile-open",
			"onCloseMobile",
			"onSidebarToggle",
			"user",
			"stats"
		]),
		createBaseVNode("main", { class: normalizeClass(["transition-all duration-300 min-h-screen", $data.isSidebarCollapsed ? "lg:ml-16" : "lg:ml-56"]) }, [createBaseVNode("header", _hoisted_4, [createBaseVNode("div", _hoisted_5, [createBaseVNode("div", _hoisted_6, [
			createBaseVNode("button", {
				onClick: _cache[0] || (_cache[0] = (...args) => $options.toggleMobileSidebar && $options.toggleMobileSidebar(...args)),
				class: "lg:hidden p-2 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors"
			}, [!$data.isMobileSidebarOpen ? (openBlock(), createElementBlock("svg", _hoisted_7, [..._cache[8] || (_cache[8] = [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M4 6h16M4 12h16M4 18h16"
			}, null, -1)])])) : (openBlock(), createElementBlock("svg", _hoisted_8, [..._cache[9] || (_cache[9] = [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M6 18L18 6M6 6l12 12"
			}, null, -1)])]))]),
			createBaseVNode("div", _hoisted_9, [
				_cache[10] || (_cache[10] = createBaseVNode("svg", {
					class: "w-4 h-4 text-slate-400 dark:text-slate-500",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" })], -1)),
				_cache[11] || (_cache[11] = createBaseVNode("span", { class: "text-slate-400 dark:text-slate-500" }, "/", -1)),
				createBaseVNode("span", _hoisted_10, toDisplayString($data.activeComponent.replace(/([A-Z])/g, " $1").trim()), 1)
			]),
			createBaseVNode("div", _hoisted_11, [
				withDirectives(createBaseVNode("input", {
					"onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => $data.globalSearch = $event),
					onFocus: _cache[2] || (_cache[2] = ($event) => $data.showSearchResults = true),
					onBlur: _cache[3] || (_cache[3] = (...args) => $options.hideSearchResults && $options.hideSearchResults(...args)),
					type: "text",
					placeholder: "Search...",
					class: "w-full pl-9 pr-4 py-2 text-sm bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 transition-all"
				}, null, 544), [[vModelText, $data.globalSearch]]),
				_cache[12] || (_cache[12] = createBaseVNode("svg", {
					class: "w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400",
					fill: "none",
					stroke: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", {
					"stroke-linecap": "round",
					"stroke-linejoin": "round",
					"stroke-width": "2",
					d: "M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
				})], -1)),
				$data.showSearchResults && $data.globalSearch ? (openBlock(), createElementBlock("div", _hoisted_12, [$options.searchResults.length === 0 ? (openBlock(), createElementBlock("div", _hoisted_13, " No results found ")) : createCommentVNode("", true), (openBlock(true), createElementBlock(Fragment, null, renderList($options.searchResults, (result) => {
					return openBlock(), createElementBlock("button", {
						key: result.id,
						onMousedown: ($event) => $options.navigateToResult(result),
						class: "w-full px-4 py-3 text-left hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors border-b border-slate-100 dark:border-slate-700 last:border-0"
					}, [createBaseVNode("div", _hoisted_15, [createBaseVNode("span", _hoisted_16, toDisplayString(result.icon), 1), createBaseVNode("div", _hoisted_17, [createBaseVNode("p", _hoisted_18, toDisplayString(result.title), 1), createBaseVNode("p", _hoisted_19, toDisplayString(result.subtitle), 1)])])], 40, _hoisted_14);
				}), 128))])) : createCommentVNode("", true)
			])
		]), createBaseVNode("div", _hoisted_20, [createBaseVNode("div", _hoisted_21, [createBaseVNode("button", {
			onClick: _cache[4] || (_cache[4] = (...args) => $options.toggleNotifications && $options.toggleNotifications(...args)),
			class: "relative p-2 rounded-lg bg-gradient-to-r from-emerald-500/90 to-green-600/90 text-white hover:from-emerald-600 hover:to-green-700 transition-all shadow-md hover:shadow-lg"
		}, [_cache[13] || (_cache[13] = createBaseVNode("svg", {
			class: "w-5 h-5",
			fill: "none",
			stroke: "currentColor",
			viewBox: "0 0 24 24"
		}, [createBaseVNode("path", {
			"stroke-linecap": "round",
			"stroke-linejoin": "round",
			"stroke-width": "2",
			d: "M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
		})], -1)), $options.unreadNotifications > 0 ? (openBlock(), createElementBlock("span", _hoisted_22, toDisplayString($options.unreadNotifications > 9 ? "9+" : $options.unreadNotifications), 1)) : createCommentVNode("", true)]), $data.showNotifications ? (openBlock(), createElementBlock("div", _hoisted_23, [createBaseVNode("div", _hoisted_24, [_cache[14] || (_cache[14] = createBaseVNode("h3", { class: "text-sm font-semibold text-slate-900 dark:text-white" }, "Notifications", -1)), createBaseVNode("button", {
			onClick: _cache[5] || (_cache[5] = (...args) => $options.markAllAsRead && $options.markAllAsRead(...args)),
			class: "text-xs text-blue-600 dark:text-blue-400 hover:underline"
		}, "Mark all read")]), createBaseVNode("div", _hoisted_25, [$data.notifications.length === 0 ? (openBlock(), createElementBlock("div", _hoisted_26, " No notifications ")) : createCommentVNode("", true), (openBlock(true), createElementBlock(Fragment, null, renderList($data.notifications, (notif) => {
			return openBlock(), createElementBlock("button", {
				key: notif.id,
				onClick: ($event) => $options.handleNotificationClick(notif),
				class: normalizeClass(["w-full px-4 py-3 text-left hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors border-b border-slate-100 dark:border-slate-700 last:border-0", { "bg-blue-50 dark:bg-blue-500/10": !notif.read }])
			}, [createBaseVNode("div", _hoisted_28, [
				_cache[15] || (_cache[15] = createBaseVNode("svg", {
					class: "w-5 h-5 text-blue-500 mt-0.5",
					fill: "currentColor",
					viewBox: "0 0 24 24"
				}, [createBaseVNode("path", { d: "M12 22c1.1 0 2-.9 2-2h-4c0 1.1.89 2 2 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z" })], -1)),
				createBaseVNode("div", _hoisted_29, [
					createBaseVNode("p", _hoisted_30, toDisplayString(notif.title), 1),
					createBaseVNode("p", _hoisted_31, toDisplayString(notif.message), 1),
					createBaseVNode("p", _hoisted_32, toDisplayString(notif.time), 1)
				]),
				!notif.read ? (openBlock(), createElementBlock("div", _hoisted_33)) : createCommentVNode("", true)
			])], 10, _hoisted_27);
		}), 128))])])) : createCommentVNode("", true)]), createBaseVNode("div", _hoisted_34, [createBaseVNode("button", {
			onClick: _cache[6] || (_cache[6] = (...args) => $options.toggleUserMenu && $options.toggleUserMenu(...args)),
			class: "flex items-center space-x-3 p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
		}, [
			_cache[16] || (_cache[16] = createBaseVNode("svg", {
				class: "w-8 h-8 text-slate-600 dark:text-slate-400",
				fill: "none",
				stroke: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
			})], -1)),
			createBaseVNode("div", _hoisted_35, [createBaseVNode("p", _hoisted_36, toDisplayString($data.user?.username), 1), createBaseVNode("p", _hoisted_37, toDisplayString($data.user?.role || "Admin"), 1)]),
			_cache[17] || (_cache[17] = createBaseVNode("svg", {
				class: "w-4 h-4 text-slate-400",
				fill: "none",
				stroke: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M19 9l-7 7-7-7"
			})], -1))
		]), $data.showUserMenu ? (openBlock(), createElementBlock("div", _hoisted_38, [
			createBaseVNode("div", _hoisted_39, [createBaseVNode("p", _hoisted_40, toDisplayString($data.user?.username), 1), createBaseVNode("p", _hoisted_41, toDisplayString($data.user?.email || "admin@teralinkx.com"), 1)]),
			_cache[19] || (_cache[19] = createStaticVNode("<div class=\"py-2\"><button class=\"w-full px-4 py-2 text-left text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors flex items-center space-x-2\"><svg class=\"w-4 h-4\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z\"></path></svg><span>Profile</span></button><button class=\"w-full px-4 py-2 text-left text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors flex items-center space-x-2\"><svg class=\"w-4 h-4\" fill=\"currentColor\" viewBox=\"0 0 24 24\"><path d=\"M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11.03L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.22,8.95 2.27,9.22 2.46,9.37L4.57,11.03C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.22,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.68 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z\"></path></svg><span>Settings</span></button><button class=\"w-full px-4 py-2 text-left text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors flex items-center space-x-2\"><svg class=\"w-4 h-4\" fill=\"none\" stroke=\"currentColor\" viewBox=\"0 0 24 24\"><path stroke-linecap=\"round\" stroke-linejoin=\"round\" stroke-width=\"2\" d=\"M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9\"></path></svg><span>Preferences</span></button></div>", 1)),
			createBaseVNode("div", _hoisted_42, [createBaseVNode("button", {
				onClick: _cache[7] || (_cache[7] = (...args) => $options.handleLogout && $options.handleLogout(...args)),
				class: "w-full px-4 py-2 text-left text-sm text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-500/10 transition-colors flex items-center space-x-2"
			}, [..._cache[18] || (_cache[18] = [createBaseVNode("svg", {
				class: "w-4 h-4",
				fill: "none",
				stroke: "currentColor",
				viewBox: "0 0 24 24"
			}, [createBaseVNode("path", {
				"stroke-linecap": "round",
				"stroke-linejoin": "round",
				"stroke-width": "2",
				d: "M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
			})], -1), createBaseVNode("span", null, "Logout", -1)])])])
		])) : createCommentVNode("", true)])])])]), createBaseVNode("div", _hoisted_43, [createVNode(Transition, {
			name: "component-fade",
			mode: "out-in"
		}, {
			default: withCtx(() => [(openBlock(), createBlock(resolveDynamicComponent($data.activeComponent), { key: $data.activeComponent }))]),
			_: 1
		})])], 2),
		createVNode(_component_RealTimeNotifications),
		$data.showToast ? (openBlock(), createElementBlock("div", _hoisted_44, [createBaseVNode("div", _hoisted_45, [_cache[20] || (_cache[20] = createBaseVNode("div", { class: "w-1.5 h-1.5 bg-white rounded-full animate-pulse" }, null, -1)), createBaseVNode("span", _hoisted_46, toDisplayString($data.toastMessage), 1)])])) : createCommentVNode("", true)
	])) : (openBlock(), createBlock(_component_Auth, {
		key: 1,
		onLoginSuccess: $options.handleLoginSuccess
	}, null, 8, ["onLoginSuccess"]))])) : (openBlock(), createElementBlock("div", _hoisted_47, [..._cache[21] || (_cache[21] = [createBaseVNode("div", { class: "text-center" }, [
		createBaseVNode("div", { class: "w-12 h-12 border-3 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" }),
		createBaseVNode("p", { class: "text-slate-900 dark:text-white font-medium" }, "Checking authentication..."),
		createBaseVNode("p", { class: "text-slate-500 dark:text-slate-400 text-sm mt-2" }, "Please wait")
	], -1)])]))]);
}
var App_default = /* @__PURE__ */ __plugin_vue_export_helper_default(_sfc_main, [["render", _sfc_render]]);
var scriptRel = "modulepreload";
var assetsURL = function(dep) {
	return "/su/" + dep;
};
var seen = {};
const __vitePreload = function preload(baseModule, deps, importerUrl) {
	let promise = Promise.resolve();
	if (deps && deps.length > 0) {
		const links = document.getElementsByTagName("link");
		const cspNonceMeta = document.querySelector("meta[property=csp-nonce]");
		const cspNonce = cspNonceMeta?.nonce || cspNonceMeta?.getAttribute("nonce");
		function allSettled(promises$2) {
			return Promise.all(promises$2.map((p) => Promise.resolve(p).then((value$1) => ({
				status: "fulfilled",
				value: value$1
			}), (reason) => ({
				status: "rejected",
				reason
			}))));
		}
		promise = allSettled(deps.map((dep) => {
			dep = assetsURL(dep, importerUrl);
			if (dep in seen) return;
			seen[dep] = true;
			const isCss = dep.endsWith(".css");
			const cssSelector = isCss ? "[rel=\"stylesheet\"]" : "";
			if (!!importerUrl) for (let i$1 = links.length - 1; i$1 >= 0; i$1--) {
				const link$1 = links[i$1];
				if (link$1.href === dep && (!isCss || link$1.rel === "stylesheet")) return;
			}
			else if (document.querySelector(`link[href="${dep}"]${cssSelector}`)) return;
			const link = document.createElement("link");
			link.rel = isCss ? "stylesheet" : scriptRel;
			if (!isCss) link.as = "script";
			link.crossOrigin = "";
			link.href = dep;
			if (cspNonce) link.setAttribute("nonce", cspNonce);
			document.head.appendChild(link);
			if (isCss) return new Promise((res, rej) => {
				link.addEventListener("load", res);
				link.addEventListener("error", () => rej(/* @__PURE__ */ new Error(`Unable to preload CSS for ${dep}`)));
			});
		}));
	}
	function handlePreloadError(err$2) {
		const e$1 = new Event("vite:preloadError", { cancelable: true });
		e$1.payload = err$2;
		window.dispatchEvent(e$1);
		if (!e$1.defaultPrevented) throw err$2;
	}
	return promise.then((res) => {
		for (const item of res || []) {
			if (item.status !== "rejected") continue;
			handlePreloadError(item.reason);
		}
		return baseModule().catch(handlePreloadError);
	});
};
var router_default = createRouter({
	history: createWebHistory(),
	routes: [
		{
			path: "/",
			name: "Auth",
			component: () => __vitePreload(() => import("./Auth-DRKe7qZ-.js"), __vite__mapDeps([0,1,2])),
			meta: { requiresAuth: false }
		},
		{
			path: "/dashboard",
			name: "Dashboard",
			component: () => __vitePreload(() => import("./Dashboard-GPgSYzCF.js"), __vite__mapDeps([3,1,2,4,5])),
			meta: { requiresAuth: true }
		},
		{
			path: "/clients",
			name: "Clients",
			component: () => __vitePreload(() => import("./Clients-D0WDNodq.js"), __vite__mapDeps([6,1,2,4,5])),
			meta: { requiresAuth: true }
		},
		{
			path: "/users",
			name: "Users",
			component: () => __vitePreload(() => import("./Users-DxFJBfet.js"), __vite__mapDeps([7,1,2,4,5])),
			meta: { requiresAuth: true }
		},
		{
			path: "/devices",
			name: "Devices",
			component: () => __vitePreload(() => import("./Devices-CdBilu0F.js"), __vite__mapDeps([8,1,2,4,5])),
			meta: { requiresAuth: true }
		},
		{
			path: "/sessions",
			name: "Sessions",
			component: () => __vitePreload(() => import("./Sessions-ieNgBXfP.js"), __vite__mapDeps([9,1,2,4,5])),
			meta: { requiresAuth: true }
		},
		{
			path: "/packages",
			name: "Packages",
			component: () => __vitePreload(() => import("./Packages-CPV9tkk6.js"), __vite__mapDeps([10,1,2,4,5])),
			meta: { requiresAuth: true }
		},
		{
			path: "/vouchers",
			name: "Vouchers",
			component: () => __vitePreload(() => import("./Vouchers-t6ZdL_at.js"), __vite__mapDeps([11,1,2,4,5])),
			meta: { requiresAuth: true }
		},
		{
			path: "/coupons",
			name: "Coupons",
			component: () => __vitePreload(() => import("./Coupons-McJaEr4y.js"), __vite__mapDeps([12,1,2,4,5])),
			meta: { requiresAuth: true }
		},
		{
			path: "/promotions",
			name: "Promotions",
			component: () => __vitePreload(() => import("./Promotions-BMvV-8SB.js"), __vite__mapDeps([13,1,2,4,5])),
			meta: { requiresAuth: true }
		},
		{
			path: "/point-transactions",
			name: "PointTransactions",
			component: () => __vitePreload(() => import("./PointTransactions-CvXFc106.js"), __vite__mapDeps([14,1,2,4,5])),
			meta: { requiresAuth: true }
		},
		{
			path: "/locations",
			name: "Locations",
			component: () => __vitePreload(() => import("./Locations-CRz5OZic.js"), __vite__mapDeps([15,1,2,4,5])),
			meta: { requiresAuth: true }
		},
		{
			path: "/transactions",
			name: "Transactions",
			component: () => __vitePreload(() => import("./Transactions-Dj-DLjwB.js"), __vite__mapDeps([16,1,2,4,5])),
			meta: { requiresAuth: true }
		},
		{
			path: "/refunds",
			name: "Refunds",
			component: () => __vitePreload(() => import("./Refunds-DdutsYds.js"), __vite__mapDeps([17,1,2,4,5])),
			meta: { requiresAuth: true }
		}
	],
	scrollBehavior(to, from, savedPosition) {
		if (savedPosition) return savedPosition;
		return {
			top: 0,
			behavior: "smooth"
		};
	}
});
var app = createApp(App_default);
var pinia = createPinia();
app.use(pinia);
app.use(router_default);
app.config.performance = true;
app.config.errorHandler = (err) => {};
app.mount("#app");
export { PointTransactions_default as a, Vouchers_default as c, Devices_default as d, Users_default as f, Locations_default as i, Packages_default as l, Dashboard_default as m, Refunds_default as n, Promotions_default as o, Clients_default as p, Transactions_default as r, Coupons_default as s, Auth_default as t, Sessions_default as u };
