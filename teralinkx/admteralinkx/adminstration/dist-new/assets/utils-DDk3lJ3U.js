import { n as __export, t as __commonJSMin } from "./rolldown-runtime-DGruFWvd.js";
var require_pusher = /* @__PURE__ */ __commonJSMin(((exports, module) => {
	/*!
	* Pusher JavaScript Library v8.4.0
	* https://pusher.com/
	*
	* Copyright 2020, Pusher
	* Released under the MIT licence.
	*/
	(function webpackUniversalModuleDefinition(root, factory$1) {
		if (typeof exports === "object" && typeof module === "object") module.exports = factory$1();
		else if (typeof define === "function" && define.amd) define([], factory$1);
		else if (typeof exports === "object") exports["Pusher"] = factory$1();
		else root["Pusher"] = factory$1();
	})(window, function() {
		return (function(modules) {
			var installedModules = {};
			function __webpack_require__(moduleId) {
				if (installedModules[moduleId]) return installedModules[moduleId].exports;
				var module$1 = installedModules[moduleId] = {
					i: moduleId,
					l: false,
					exports: {}
				};
				modules[moduleId].call(module$1.exports, module$1, module$1.exports, __webpack_require__);
				module$1.l = true;
				return module$1.exports;
			}
			__webpack_require__.m = modules;
			__webpack_require__.c = installedModules;
			__webpack_require__.d = function(exports$1, name, getter) {
				if (!__webpack_require__.o(exports$1, name)) Object.defineProperty(exports$1, name, {
					enumerable: true,
					get: getter
				});
			};
			__webpack_require__.r = function(exports$1) {
				if (typeof Symbol !== "undefined" && Symbol.toStringTag) Object.defineProperty(exports$1, Symbol.toStringTag, { value: "Module" });
				Object.defineProperty(exports$1, "__esModule", { value: true });
			};
			__webpack_require__.t = function(value, mode) {
				if (mode & 1) value = __webpack_require__(value);
				if (mode & 8) return value;
				if (mode & 4 && typeof value === "object" && value && value.__esModule) return value;
				var ns = Object.create(null);
				__webpack_require__.r(ns);
				Object.defineProperty(ns, "default", {
					enumerable: true,
					value
				});
				if (mode & 2 && typeof value != "string") for (var key in value) __webpack_require__.d(ns, key, function(key$1) {
					return value[key$1];
				}.bind(null, key));
				return ns;
			};
			__webpack_require__.n = function(module$1) {
				var getter = module$1 && module$1.__esModule ? function getDefault() {
					return module$1["default"];
				} : function getModuleExports() {
					return module$1;
				};
				__webpack_require__.d(getter, "a", getter);
				return getter;
			};
			__webpack_require__.o = function(object, property) {
				return Object.prototype.hasOwnProperty.call(object, property);
			};
			__webpack_require__.p = "";
			return __webpack_require__(__webpack_require__.s = 2);
		})([
			(function(module$1, exports$1, __webpack_require__) {
				var __extends = this && this.__extends || (function() {
					var extendStatics = function(d, b) {
						extendStatics = Object.setPrototypeOf || { __proto__: [] } instanceof Array && function(d$1, b$1) {
							d$1.__proto__ = b$1;
						} || function(d$1, b$1) {
							for (var p in b$1) if (b$1.hasOwnProperty(p)) d$1[p] = b$1[p];
						};
						return extendStatics(d, b);
					};
					return function(d, b) {
						extendStatics(d, b);
						function __() {
							this.constructor = d;
						}
						d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
					};
				})();
				Object.defineProperty(exports$1, "__esModule", { value: true });
				var INVALID_BYTE = 256;
				var Coder = function() {
					function Coder$1(_paddingCharacter) {
						if (_paddingCharacter === void 0) _paddingCharacter = "=";
						this._paddingCharacter = _paddingCharacter;
					}
					Coder$1.prototype.encodedLength = function(length) {
						if (!this._paddingCharacter) return (length * 8 + 5) / 6 | 0;
						return (length + 2) / 3 * 4 | 0;
					};
					Coder$1.prototype.encode = function(data) {
						var out = "";
						var i = 0;
						for (; i < data.length - 2; i += 3) {
							var c = data[i] << 16 | data[i + 1] << 8 | data[i + 2];
							out += this._encodeByte(c >>> 18 & 63);
							out += this._encodeByte(c >>> 12 & 63);
							out += this._encodeByte(c >>> 6 & 63);
							out += this._encodeByte(c >>> 0 & 63);
						}
						var left = data.length - i;
						if (left > 0) {
							var c = data[i] << 16 | (left === 2 ? data[i + 1] << 8 : 0);
							out += this._encodeByte(c >>> 18 & 63);
							out += this._encodeByte(c >>> 12 & 63);
							if (left === 2) out += this._encodeByte(c >>> 6 & 63);
							else out += this._paddingCharacter || "";
							out += this._paddingCharacter || "";
						}
						return out;
					};
					Coder$1.prototype.maxDecodedLength = function(length) {
						if (!this._paddingCharacter) return (length * 6 + 7) / 8 | 0;
						return length / 4 * 3 | 0;
					};
					Coder$1.prototype.decodedLength = function(s) {
						return this.maxDecodedLength(s.length - this._getPaddingLength(s));
					};
					Coder$1.prototype.decode = function(s) {
						if (s.length === 0) return new Uint8Array(0);
						var paddingLength = this._getPaddingLength(s);
						var length = s.length - paddingLength;
						var out = new Uint8Array(this.maxDecodedLength(length));
						var op = 0;
						var i = 0;
						var haveBad = 0;
						var v0 = 0, v1 = 0, v2 = 0, v3 = 0;
						for (; i < length - 4; i += 4) {
							v0 = this._decodeChar(s.charCodeAt(i + 0));
							v1 = this._decodeChar(s.charCodeAt(i + 1));
							v2 = this._decodeChar(s.charCodeAt(i + 2));
							v3 = this._decodeChar(s.charCodeAt(i + 3));
							out[op++] = v0 << 2 | v1 >>> 4;
							out[op++] = v1 << 4 | v2 >>> 2;
							out[op++] = v2 << 6 | v3;
							haveBad |= v0 & INVALID_BYTE;
							haveBad |= v1 & INVALID_BYTE;
							haveBad |= v2 & INVALID_BYTE;
							haveBad |= v3 & INVALID_BYTE;
						}
						if (i < length - 1) {
							v0 = this._decodeChar(s.charCodeAt(i));
							v1 = this._decodeChar(s.charCodeAt(i + 1));
							out[op++] = v0 << 2 | v1 >>> 4;
							haveBad |= v0 & INVALID_BYTE;
							haveBad |= v1 & INVALID_BYTE;
						}
						if (i < length - 2) {
							v2 = this._decodeChar(s.charCodeAt(i + 2));
							out[op++] = v1 << 4 | v2 >>> 2;
							haveBad |= v2 & INVALID_BYTE;
						}
						if (i < length - 3) {
							v3 = this._decodeChar(s.charCodeAt(i + 3));
							out[op++] = v2 << 6 | v3;
							haveBad |= v3 & INVALID_BYTE;
						}
						if (haveBad !== 0) throw new Error("Base64Coder: incorrect characters for decoding");
						return out;
					};
					Coder$1.prototype._encodeByte = function(b) {
						var result = b;
						result += 65;
						result += 25 - b >>> 8 & 6;
						result += 51 - b >>> 8 & -75;
						result += 61 - b >>> 8 & -15;
						result += 62 - b >>> 8 & 3;
						return String.fromCharCode(result);
					};
					Coder$1.prototype._decodeChar = function(c) {
						var result = INVALID_BYTE;
						result += (42 - c & c - 44) >>> 8 & -INVALID_BYTE + c - 43 + 62;
						result += (46 - c & c - 48) >>> 8 & -INVALID_BYTE + c - 47 + 63;
						result += (47 - c & c - 58) >>> 8 & -INVALID_BYTE + c - 48 + 52;
						result += (64 - c & c - 91) >>> 8 & -INVALID_BYTE + c - 65 + 0;
						result += (96 - c & c - 123) >>> 8 & -INVALID_BYTE + c - 97 + 26;
						return result;
					};
					Coder$1.prototype._getPaddingLength = function(s) {
						var paddingLength = 0;
						if (this._paddingCharacter) {
							for (var i = s.length - 1; i >= 0; i--) {
								if (s[i] !== this._paddingCharacter) break;
								paddingLength++;
							}
							if (s.length < 4 || paddingLength > 2) throw new Error("Base64Coder: incorrect padding");
						}
						return paddingLength;
					};
					return Coder$1;
				}();
				exports$1.Coder = Coder;
				var stdCoder = new Coder();
				function encode$2(data) {
					return stdCoder.encode(data);
				}
				exports$1.encode = encode$2;
				function decode(s) {
					return stdCoder.decode(s);
				}
				exports$1.decode = decode;
				var URLSafeCoder = function(_super) {
					__extends(URLSafeCoder$1, _super);
					function URLSafeCoder$1() {
						return _super !== null && _super.apply(this, arguments) || this;
					}
					URLSafeCoder$1.prototype._encodeByte = function(b) {
						var result = b;
						result += 65;
						result += 25 - b >>> 8 & 6;
						result += 51 - b >>> 8 & -75;
						result += 61 - b >>> 8 & -13;
						result += 62 - b >>> 8 & 49;
						return String.fromCharCode(result);
					};
					URLSafeCoder$1.prototype._decodeChar = function(c) {
						var result = INVALID_BYTE;
						result += (44 - c & c - 46) >>> 8 & -INVALID_BYTE + c - 45 + 62;
						result += (94 - c & c - 96) >>> 8 & -INVALID_BYTE + c - 95 + 63;
						result += (47 - c & c - 58) >>> 8 & -INVALID_BYTE + c - 48 + 52;
						result += (64 - c & c - 91) >>> 8 & -INVALID_BYTE + c - 65 + 0;
						result += (96 - c & c - 123) >>> 8 & -INVALID_BYTE + c - 97 + 26;
						return result;
					};
					return URLSafeCoder$1;
				}(Coder);
				exports$1.URLSafeCoder = URLSafeCoder;
				var urlSafeCoder = new URLSafeCoder();
				function encodeURLSafe(data) {
					return urlSafeCoder.encode(data);
				}
				exports$1.encodeURLSafe = encodeURLSafe;
				function decodeURLSafe(s) {
					return urlSafeCoder.decode(s);
				}
				exports$1.decodeURLSafe = decodeURLSafe;
				exports$1.encodedLength = function(length) {
					return stdCoder.encodedLength(length);
				};
				exports$1.maxDecodedLength = function(length) {
					return stdCoder.maxDecodedLength(length);
				};
				exports$1.decodedLength = function(s) {
					return stdCoder.decodedLength(s);
				};
			}),
			(function(module$1, exports$1, __webpack_require__) {
				Object.defineProperty(exports$1, "__esModule", { value: true });
				var INVALID_UTF16 = "utf8: invalid string";
				var INVALID_UTF8 = "utf8: invalid source encoding";
				function encode$2(s) {
					var arr = new Uint8Array(encodedLength(s));
					var pos = 0;
					for (var i = 0; i < s.length; i++) {
						var c = s.charCodeAt(i);
						if (c < 128) arr[pos++] = c;
						else if (c < 2048) {
							arr[pos++] = 192 | c >> 6;
							arr[pos++] = 128 | c & 63;
						} else if (c < 55296) {
							arr[pos++] = 224 | c >> 12;
							arr[pos++] = 128 | c >> 6 & 63;
							arr[pos++] = 128 | c & 63;
						} else {
							i++;
							c = (c & 1023) << 10;
							c |= s.charCodeAt(i) & 1023;
							c += 65536;
							arr[pos++] = 240 | c >> 18;
							arr[pos++] = 128 | c >> 12 & 63;
							arr[pos++] = 128 | c >> 6 & 63;
							arr[pos++] = 128 | c & 63;
						}
					}
					return arr;
				}
				exports$1.encode = encode$2;
				function encodedLength(s) {
					var result = 0;
					for (var i = 0; i < s.length; i++) {
						var c = s.charCodeAt(i);
						if (c < 128) result += 1;
						else if (c < 2048) result += 2;
						else if (c < 55296) result += 3;
						else if (c <= 57343) {
							if (i >= s.length - 1) throw new Error(INVALID_UTF16);
							i++;
							result += 4;
						} else throw new Error(INVALID_UTF16);
					}
					return result;
				}
				exports$1.encodedLength = encodedLength;
				function decode(arr) {
					var chars = [];
					for (var i = 0; i < arr.length; i++) {
						var b = arr[i];
						if (b & 128) {
							var min = void 0;
							if (b < 224) {
								if (i >= arr.length) throw new Error(INVALID_UTF8);
								var n1 = arr[++i];
								if ((n1 & 192) !== 128) throw new Error(INVALID_UTF8);
								b = (b & 31) << 6 | n1 & 63;
								min = 128;
							} else if (b < 240) {
								if (i >= arr.length - 1) throw new Error(INVALID_UTF8);
								var n1 = arr[++i];
								var n2 = arr[++i];
								if ((n1 & 192) !== 128 || (n2 & 192) !== 128) throw new Error(INVALID_UTF8);
								b = (b & 15) << 12 | (n1 & 63) << 6 | n2 & 63;
								min = 2048;
							} else if (b < 248) {
								if (i >= arr.length - 2) throw new Error(INVALID_UTF8);
								var n1 = arr[++i];
								var n2 = arr[++i];
								var n3 = arr[++i];
								if ((n1 & 192) !== 128 || (n2 & 192) !== 128 || (n3 & 192) !== 128) throw new Error(INVALID_UTF8);
								b = (b & 15) << 18 | (n1 & 63) << 12 | (n2 & 63) << 6 | n3 & 63;
								min = 65536;
							} else throw new Error(INVALID_UTF8);
							if (b < min || b >= 55296 && b <= 57343) throw new Error(INVALID_UTF8);
							if (b >= 65536) {
								if (b > 1114111) throw new Error(INVALID_UTF8);
								b -= 65536;
								chars.push(String.fromCharCode(55296 | b >> 10));
								b = 56320 | b & 1023;
							}
						}
						chars.push(String.fromCharCode(b));
					}
					return chars.join("");
				}
				exports$1.decode = decode;
			}),
			(function(module$1, exports$1, __webpack_require__) {
				module$1.exports = __webpack_require__(3).default;
			}),
			(function(module$1, __webpack_exports__, __webpack_require__) {
				__webpack_require__.r(__webpack_exports__);
				class ScriptReceiverFactory {
					constructor(prefix$1, name) {
						this.lastId = 0;
						this.prefix = prefix$1;
						this.name = name;
					}
					create(callback) {
						this.lastId++;
						var number = this.lastId;
						var id = this.prefix + number;
						var name = this.name + "[" + number + "]";
						var called = false;
						var callbackWrapper = function() {
							if (!called) {
								callback.apply(null, arguments);
								called = true;
							}
						};
						this[number] = callbackWrapper;
						return {
							number,
							id,
							name,
							callback: callbackWrapper
						};
					}
					remove(receiver) {
						delete this[receiver.number];
					}
				}
				var ScriptReceivers = new ScriptReceiverFactory("_pusher_script_", "Pusher.ScriptReceivers");
				var defaults$1 = {
					VERSION: "8.4.0",
					PROTOCOL: 7,
					wsPort: 80,
					wssPort: 443,
					wsPath: "",
					httpHost: "sockjs.pusher.com",
					httpPort: 80,
					httpsPort: 443,
					httpPath: "/pusher",
					stats_host: "stats.pusher.com",
					authEndpoint: "/pusher/auth",
					authTransport: "ajax",
					activityTimeout: 12e4,
					pongTimeout: 3e4,
					unavailableTimeout: 1e4,
					userAuthentication: {
						endpoint: "/pusher/user-auth",
						transport: "ajax"
					},
					channelAuthorization: {
						endpoint: "/pusher/auth",
						transport: "ajax"
					},
					cdn_http: "http://js.pusher.com",
					cdn_https: "https://js.pusher.com",
					dependency_suffix: ""
				};
				class dependency_loader_DependencyLoader {
					constructor(options) {
						this.options = options;
						this.receivers = options.receivers || ScriptReceivers;
						this.loading = {};
					}
					load(name, options, callback) {
						var self$1 = this;
						if (self$1.loading[name] && self$1.loading[name].length > 0) self$1.loading[name].push(callback);
						else {
							self$1.loading[name] = [callback];
							var request = runtime.createScriptRequest(self$1.getPath(name, options));
							var receiver = self$1.receivers.create(function(error) {
								self$1.receivers.remove(receiver);
								if (self$1.loading[name]) {
									var callbacks = self$1.loading[name];
									delete self$1.loading[name];
									var successCallback = function(wasSuccessful) {
										if (!wasSuccessful) request.cleanup();
									};
									for (var i = 0; i < callbacks.length; i++) callbacks[i](error, successCallback);
								}
							});
							request.send(receiver);
						}
					}
					getRoot(options) {
						var cdn;
						var protocol = runtime.getDocument().location.protocol;
						if (options && options.useTLS || protocol === "https:") cdn = this.options.cdn_https;
						else cdn = this.options.cdn_http;
						return cdn.replace(/\/*$/, "") + "/" + this.options.version;
					}
					getPath(name, options) {
						return this.getRoot(options) + "/" + name + this.options.suffix + ".js";
					}
				}
				var DependenciesReceivers = new ScriptReceiverFactory("_pusher_dependencies", "Pusher.DependenciesReceivers");
				var Dependencies = new dependency_loader_DependencyLoader({
					cdn_http: defaults$1.cdn_http,
					cdn_https: defaults$1.cdn_https,
					version: defaults$1.VERSION,
					suffix: defaults$1.dependency_suffix,
					receivers: DependenciesReceivers
				});
				const urlStore = {
					baseUrl: "https://pusher.com",
					urls: {
						authenticationEndpoint: { path: "/docs/channels/server_api/authenticating_users" },
						authorizationEndpoint: { path: "/docs/channels/server_api/authorizing-users/" },
						javascriptQuickStart: { path: "/docs/javascript_quick_start" },
						triggeringClientEvents: { path: "/docs/client_api_guide/client_events#trigger-events" },
						encryptedChannelSupport: { fullUrl: "https://github.com/pusher/pusher-js/tree/cc491015371a4bde5743d1c87a0fbac0feb53195#encrypted-channel-support" }
					}
				};
				const buildLogSuffix = function(key) {
					const urlPrefix = "See:";
					const urlObj = urlStore.urls[key];
					if (!urlObj) return "";
					let url;
					if (urlObj.fullUrl) url = urlObj.fullUrl;
					else if (urlObj.path) url = urlStore.baseUrl + urlObj.path;
					if (!url) return "";
					return `${urlPrefix} ${url}`;
				};
				var url_store = { buildLogSuffix };
				var AuthRequestType;
				(function(AuthRequestType$1) {
					AuthRequestType$1["UserAuthentication"] = "user-authentication";
					AuthRequestType$1["ChannelAuthorization"] = "channel-authorization";
				})(AuthRequestType || (AuthRequestType = {}));
				class BadEventName extends Error {
					constructor(msg) {
						super(msg);
						Object.setPrototypeOf(this, new.target.prototype);
					}
				}
				class BadChannelName extends Error {
					constructor(msg) {
						super(msg);
						Object.setPrototypeOf(this, new.target.prototype);
					}
				}
				class RequestTimedOut extends Error {
					constructor(msg) {
						super(msg);
						Object.setPrototypeOf(this, new.target.prototype);
					}
				}
				class TransportPriorityTooLow extends Error {
					constructor(msg) {
						super(msg);
						Object.setPrototypeOf(this, new.target.prototype);
					}
				}
				class TransportClosed extends Error {
					constructor(msg) {
						super(msg);
						Object.setPrototypeOf(this, new.target.prototype);
					}
				}
				class UnsupportedFeature extends Error {
					constructor(msg) {
						super(msg);
						Object.setPrototypeOf(this, new.target.prototype);
					}
				}
				class UnsupportedTransport extends Error {
					constructor(msg) {
						super(msg);
						Object.setPrototypeOf(this, new.target.prototype);
					}
				}
				class UnsupportedStrategy extends Error {
					constructor(msg) {
						super(msg);
						Object.setPrototypeOf(this, new.target.prototype);
					}
				}
				class HTTPAuthError extends Error {
					constructor(status, msg) {
						super(msg);
						this.status = status;
						Object.setPrototypeOf(this, new.target.prototype);
					}
				}
				const ajax = function(context, query, authOptions, authRequestType, callback) {
					const xhr = runtime.createXHR();
					xhr.open("POST", authOptions.endpoint, true);
					xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
					for (var headerName in authOptions.headers) xhr.setRequestHeader(headerName, authOptions.headers[headerName]);
					if (authOptions.headersProvider != null) {
						let dynamicHeaders = authOptions.headersProvider();
						for (var headerName in dynamicHeaders) xhr.setRequestHeader(headerName, dynamicHeaders[headerName]);
					}
					xhr.onreadystatechange = function() {
						if (xhr.readyState === 4) if (xhr.status === 200) {
							let data;
							let parsed = false;
							try {
								data = JSON.parse(xhr.responseText);
								parsed = true;
							} catch (e) {
								callback(new HTTPAuthError(200, `JSON returned from ${authRequestType.toString()} endpoint was invalid, yet status code was 200. Data was: ${xhr.responseText}`), null);
							}
							if (parsed) callback(null, data);
						} else {
							let suffix = "";
							switch (authRequestType) {
								case AuthRequestType.UserAuthentication:
									suffix = url_store.buildLogSuffix("authenticationEndpoint");
									break;
								case AuthRequestType.ChannelAuthorization:
									suffix = `Clients must be authorized to join private or presence channels. ${url_store.buildLogSuffix("authorizationEndpoint")}`;
									break;
							}
							callback(new HTTPAuthError(xhr.status, `Unable to retrieve auth string from ${authRequestType.toString()} endpoint - received status: ${xhr.status} from ${authOptions.endpoint}. ${suffix}`), null);
						}
					};
					xhr.send(query);
					return xhr;
				};
				var xhr_auth = ajax;
				function encode$2(s) {
					return btoa$1(utob(s));
				}
				var fromCharCode = String.fromCharCode;
				var b64chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
				var b64tab = {};
				for (var base64_i = 0, l = b64chars.length; base64_i < l; base64_i++) b64tab[b64chars.charAt(base64_i)] = base64_i;
				var cb_utob = function(c) {
					var cc = c.charCodeAt(0);
					return cc < 128 ? c : cc < 2048 ? fromCharCode(192 | cc >>> 6) + fromCharCode(128 | cc & 63) : fromCharCode(224 | cc >>> 12 & 15) + fromCharCode(128 | cc >>> 6 & 63) + fromCharCode(128 | cc & 63);
				};
				var utob = function(u) {
					return u.replace(/[^\x00-\x7F]/g, cb_utob);
				};
				var cb_encode = function(ccc) {
					var padlen = [
						0,
						2,
						1
					][ccc.length % 3];
					var ord = ccc.charCodeAt(0) << 16 | (ccc.length > 1 ? ccc.charCodeAt(1) : 0) << 8 | (ccc.length > 2 ? ccc.charCodeAt(2) : 0);
					return [
						b64chars.charAt(ord >>> 18),
						b64chars.charAt(ord >>> 12 & 63),
						padlen >= 2 ? "=" : b64chars.charAt(ord >>> 6 & 63),
						padlen >= 1 ? "=" : b64chars.charAt(ord & 63)
					].join("");
				};
				var btoa$1 = window.btoa || function(b) {
					return b.replace(/[\s\S]{1,3}/g, cb_encode);
				};
				class Timer {
					constructor(set, clear, delay, callback) {
						this.clear = clear;
						this.timer = set(() => {
							if (this.timer) this.timer = callback(this.timer);
						}, delay);
					}
					isRunning() {
						return this.timer !== null;
					}
					ensureAborted() {
						if (this.timer) {
							this.clear(this.timer);
							this.timer = null;
						}
					}
				}
				var abstract_timer = Timer;
				function timers_clearTimeout(timer) {
					window.clearTimeout(timer);
				}
				function timers_clearInterval(timer) {
					window.clearInterval(timer);
				}
				class timers_OneOffTimer extends abstract_timer {
					constructor(delay, callback) {
						super(setTimeout, timers_clearTimeout, delay, function(timer) {
							callback();
							return null;
						});
					}
				}
				class timers_PeriodicTimer extends abstract_timer {
					constructor(delay, callback) {
						super(setInterval, timers_clearInterval, delay, function(timer) {
							callback();
							return timer;
						});
					}
				}
				var util = {
					now() {
						if (Date.now) return Date.now();
						else return (/* @__PURE__ */ new Date()).valueOf();
					},
					defer(callback) {
						return new timers_OneOffTimer(0, callback);
					},
					method(name, ...args) {
						var boundArguments = Array.prototype.slice.call(arguments, 1);
						return function(object) {
							return object[name].apply(object, boundArguments.concat(arguments));
						};
					}
				};
				function extend$1(target, ...sources) {
					for (var i = 0; i < sources.length; i++) {
						var extensions = sources[i];
						for (var property in extensions) if (extensions[property] && extensions[property].constructor && extensions[property].constructor === Object) target[property] = extend$1(target[property] || {}, extensions[property]);
						else target[property] = extensions[property];
					}
					return target;
				}
				function stringify() {
					var m = ["Pusher"];
					for (var i = 0; i < arguments.length; i++) if (typeof arguments[i] === "string") m.push(arguments[i]);
					else m.push(safeJSONStringify(arguments[i]));
					return m.join(" : ");
				}
				function arrayIndexOf(array, item) {
					var nativeIndexOf = Array.prototype.indexOf;
					if (array === null) return -1;
					if (nativeIndexOf && array.indexOf === nativeIndexOf) return array.indexOf(item);
					for (var i = 0, l$1 = array.length; i < l$1; i++) if (array[i] === item) return i;
					return -1;
				}
				function objectApply(object, f) {
					for (var key in object) if (Object.prototype.hasOwnProperty.call(object, key)) f(object[key], key, object);
				}
				function keys(object) {
					var keys$1 = [];
					objectApply(object, function(_, key) {
						keys$1.push(key);
					});
					return keys$1;
				}
				function values(object) {
					var values$1 = [];
					objectApply(object, function(value) {
						values$1.push(value);
					});
					return values$1;
				}
				function apply(array, f, context) {
					for (var i = 0; i < array.length; i++) f.call(context || window, array[i], i, array);
				}
				function map(array, f) {
					var result = [];
					for (var i = 0; i < array.length; i++) result.push(f(array[i], i, array, result));
					return result;
				}
				function mapObject(object, f) {
					var result = {};
					objectApply(object, function(value, key) {
						result[key] = f(value);
					});
					return result;
				}
				function filter(array, test$1) {
					test$1 = test$1 || function(value) {
						return !!value;
					};
					var result = [];
					for (var i = 0; i < array.length; i++) if (test$1(array[i], i, array, result)) result.push(array[i]);
					return result;
				}
				function filterObject(object, test$1) {
					var result = {};
					objectApply(object, function(value, key) {
						if (test$1 && test$1(value, key, object, result) || Boolean(value)) result[key] = value;
					});
					return result;
				}
				function flatten(object) {
					var result = [];
					objectApply(object, function(value, key) {
						result.push([key, value]);
					});
					return result;
				}
				function any(array, test$1) {
					for (var i = 0; i < array.length; i++) if (test$1(array[i], i, array)) return true;
					return false;
				}
				function collections_all(array, test$1) {
					for (var i = 0; i < array.length; i++) if (!test$1(array[i], i, array)) return false;
					return true;
				}
				function encodeParamsObject(data) {
					return mapObject(data, function(value) {
						if (typeof value === "object") value = safeJSONStringify(value);
						return encodeURIComponent(encode$2(value.toString()));
					});
				}
				function buildQueryString(data) {
					return map(flatten(encodeParamsObject(filterObject(data, function(value) {
						return value !== void 0;
					}))), util.method("join", "=")).join("&");
				}
				function decycleObject(object) {
					var objects = [], paths = [];
					return (function derez(value, path) {
						var i, name, nu;
						switch (typeof value) {
							case "object":
								if (!value) return null;
								for (i = 0; i < objects.length; i += 1) if (objects[i] === value) return { $ref: paths[i] };
								objects.push(value);
								paths.push(path);
								if (Object.prototype.toString.apply(value) === "[object Array]") {
									nu = [];
									for (i = 0; i < value.length; i += 1) nu[i] = derez(value[i], path + "[" + i + "]");
								} else {
									nu = {};
									for (name in value) if (Object.prototype.hasOwnProperty.call(value, name)) nu[name] = derez(value[name], path + "[" + JSON.stringify(name) + "]");
								}
								return nu;
							case "number":
							case "string":
							case "boolean": return value;
						}
					})(object, "$");
				}
				function safeJSONStringify(source) {
					try {
						return JSON.stringify(source);
					} catch (e) {
						return JSON.stringify(decycleObject(source));
					}
				}
				class logger_Logger {
					constructor() {
						this.globalLog = (message) => {
							if (window.console && window.console.log) window.console.log(message);
						};
					}
					debug(...args) {
						this.log(this.globalLog, args);
					}
					warn(...args) {
						this.log(this.globalLogWarn, args);
					}
					error(...args) {
						this.log(this.globalLogError, args);
					}
					globalLogWarn(message) {
						if (window.console && window.console.warn) window.console.warn(message);
						else this.globalLog(message);
					}
					globalLogError(message) {
						if (window.console && window.console.error) window.console.error(message);
						else this.globalLogWarn(message);
					}
					log(defaultLoggingFunction, ...args) {
						var message = stringify.apply(this, arguments);
						if (core_pusher.log) core_pusher.log(message);
						else if (core_pusher.logToConsole) defaultLoggingFunction.bind(this)(message);
					}
				}
				var logger = new logger_Logger();
				var jsonp = function(context, query, authOptions, authRequestType, callback) {
					if (authOptions.headers !== void 0 || authOptions.headersProvider != null) logger.warn(`To send headers with the ${authRequestType.toString()} request, you must use AJAX, rather than JSONP.`);
					var callbackName = context.nextAuthCallbackID.toString();
					context.nextAuthCallbackID++;
					var document$1 = context.getDocument();
					var script = document$1.createElement("script");
					context.auth_callbacks[callbackName] = function(data) {
						callback(null, data);
					};
					var callback_name = "Pusher.auth_callbacks['" + callbackName + "']";
					script.src = authOptions.endpoint + "?callback=" + encodeURIComponent(callback_name) + "&" + query;
					var head = document$1.getElementsByTagName("head")[0] || document$1.documentElement;
					head.insertBefore(script, head.firstChild);
				};
				var jsonp_auth = jsonp;
				class ScriptRequest {
					constructor(src) {
						this.src = src;
					}
					send(receiver) {
						var self$1 = this;
						var errorString = "Error loading " + self$1.src;
						self$1.script = document.createElement("script");
						self$1.script.id = receiver.id;
						self$1.script.src = self$1.src;
						self$1.script.type = "text/javascript";
						self$1.script.charset = "UTF-8";
						if (self$1.script.addEventListener) {
							self$1.script.onerror = function() {
								receiver.callback(errorString);
							};
							self$1.script.onload = function() {
								receiver.callback(null);
							};
						} else self$1.script.onreadystatechange = function() {
							if (self$1.script.readyState === "loaded" || self$1.script.readyState === "complete") receiver.callback(null);
						};
						if (self$1.script.async === void 0 && document.attachEvent && /opera/i.test(navigator.userAgent)) {
							self$1.errorScript = document.createElement("script");
							self$1.errorScript.id = receiver.id + "_error";
							self$1.errorScript.text = receiver.name + "('" + errorString + "');";
							self$1.script.async = self$1.errorScript.async = false;
						} else self$1.script.async = true;
						var head = document.getElementsByTagName("head")[0];
						head.insertBefore(self$1.script, head.firstChild);
						if (self$1.errorScript) head.insertBefore(self$1.errorScript, self$1.script.nextSibling);
					}
					cleanup() {
						if (this.script) {
							this.script.onload = this.script.onerror = null;
							this.script.onreadystatechange = null;
						}
						if (this.script && this.script.parentNode) this.script.parentNode.removeChild(this.script);
						if (this.errorScript && this.errorScript.parentNode) this.errorScript.parentNode.removeChild(this.errorScript);
						this.script = null;
						this.errorScript = null;
					}
				}
				class jsonp_request_JSONPRequest {
					constructor(url, data) {
						this.url = url;
						this.data = data;
					}
					send(receiver) {
						if (this.request) return;
						var query = buildQueryString(this.data);
						var url = this.url + "/" + receiver.number + "?" + query;
						this.request = runtime.createScriptRequest(url);
						this.request.send(receiver);
					}
					cleanup() {
						if (this.request) this.request.cleanup();
					}
				}
				var getAgent = function(sender, useTLS) {
					return function(data, callback) {
						var url = "http" + (useTLS ? "s" : "") + "://" + (sender.host || sender.options.host) + sender.options.path;
						var request = runtime.createJSONPRequest(url, data);
						var receiver = runtime.ScriptReceivers.create(function(error, result) {
							ScriptReceivers.remove(receiver);
							request.cleanup();
							if (result && result.host) sender.host = result.host;
							if (callback) callback(error, result);
						});
						request.send(receiver);
					};
				};
				var jsonp_timeline = {
					name: "jsonp",
					getAgent
				};
				function getGenericURL(baseScheme, params, path) {
					var scheme = baseScheme + (params.useTLS ? "s" : "");
					var host = params.useTLS ? params.hostTLS : params.hostNonTLS;
					return scheme + "://" + host + path;
				}
				function getGenericPath(key, queryString) {
					return "/app/" + key + ("?protocol=" + defaults$1.PROTOCOL + "&client=js&version=" + defaults$1.VERSION + (queryString ? "&" + queryString : ""));
				}
				var ws = { getInitial: function(key, params) {
					return getGenericURL("ws", params, (params.httpPath || "") + getGenericPath(key, "flash=false"));
				} };
				var http = { getInitial: function(key, params) {
					return getGenericURL("http", params, (params.httpPath || "/pusher") + getGenericPath(key));
				} };
				var sockjs = {
					getInitial: function(key, params) {
						return getGenericURL("http", params, params.httpPath || "/pusher");
					},
					getPath: function(key, params) {
						return getGenericPath(key);
					}
				};
				class callback_registry_CallbackRegistry {
					constructor() {
						this._callbacks = {};
					}
					get(name) {
						return this._callbacks[prefix(name)];
					}
					add(name, callback, context) {
						var prefixedEventName = prefix(name);
						this._callbacks[prefixedEventName] = this._callbacks[prefixedEventName] || [];
						this._callbacks[prefixedEventName].push({
							fn: callback,
							context
						});
					}
					remove(name, callback, context) {
						if (!name && !callback && !context) {
							this._callbacks = {};
							return;
						}
						var names = name ? [prefix(name)] : keys(this._callbacks);
						if (callback || context) this.removeCallback(names, callback, context);
						else this.removeAllCallbacks(names);
					}
					removeCallback(names, callback, context) {
						apply(names, function(name) {
							this._callbacks[name] = filter(this._callbacks[name] || [], function(binding) {
								return callback && callback !== binding.fn || context && context !== binding.context;
							});
							if (this._callbacks[name].length === 0) delete this._callbacks[name];
						}, this);
					}
					removeAllCallbacks(names) {
						apply(names, function(name) {
							delete this._callbacks[name];
						}, this);
					}
				}
				function prefix(name) {
					return "_" + name;
				}
				class dispatcher_Dispatcher {
					constructor(failThrough) {
						this.callbacks = new callback_registry_CallbackRegistry();
						this.global_callbacks = [];
						this.failThrough = failThrough;
					}
					bind(eventName, callback, context) {
						this.callbacks.add(eventName, callback, context);
						return this;
					}
					bind_global(callback) {
						this.global_callbacks.push(callback);
						return this;
					}
					unbind(eventName, callback, context) {
						this.callbacks.remove(eventName, callback, context);
						return this;
					}
					unbind_global(callback) {
						if (!callback) {
							this.global_callbacks = [];
							return this;
						}
						this.global_callbacks = filter(this.global_callbacks || [], (c) => c !== callback);
						return this;
					}
					unbind_all() {
						this.unbind();
						this.unbind_global();
						return this;
					}
					emit(eventName, data, metadata) {
						for (var i = 0; i < this.global_callbacks.length; i++) this.global_callbacks[i](eventName, data);
						var callbacks = this.callbacks.get(eventName);
						var args = [];
						if (metadata) args.push(data, metadata);
						else if (data) args.push(data);
						if (callbacks && callbacks.length > 0) for (var i = 0; i < callbacks.length; i++) callbacks[i].fn.apply(callbacks[i].context || window, args);
						else if (this.failThrough) this.failThrough(eventName, data);
						return this;
					}
				}
				class transport_connection_TransportConnection extends dispatcher_Dispatcher {
					constructor(hooks, name, priority, key, options) {
						super();
						this.initialize = runtime.transportConnectionInitializer;
						this.hooks = hooks;
						this.name = name;
						this.priority = priority;
						this.key = key;
						this.options = options;
						this.state = "new";
						this.timeline = options.timeline;
						this.activityTimeout = options.activityTimeout;
						this.id = this.timeline.generateUniqueID();
					}
					handlesActivityChecks() {
						return Boolean(this.hooks.handlesActivityChecks);
					}
					supportsPing() {
						return Boolean(this.hooks.supportsPing);
					}
					connect() {
						if (this.socket || this.state !== "initialized") return false;
						var url = this.hooks.urls.getInitial(this.key, this.options);
						try {
							this.socket = this.hooks.getSocket(url, this.options);
						} catch (e) {
							util.defer(() => {
								this.onError(e);
								this.changeState("closed");
							});
							return false;
						}
						this.bindListeners();
						logger.debug("Connecting", {
							transport: this.name,
							url
						});
						this.changeState("connecting");
						return true;
					}
					close() {
						if (this.socket) {
							this.socket.close();
							return true;
						} else return false;
					}
					send(data) {
						if (this.state === "open") {
							util.defer(() => {
								if (this.socket) this.socket.send(data);
							});
							return true;
						} else return false;
					}
					ping() {
						if (this.state === "open" && this.supportsPing()) this.socket.ping();
					}
					onOpen() {
						if (this.hooks.beforeOpen) this.hooks.beforeOpen(this.socket, this.hooks.urls.getPath(this.key, this.options));
						this.changeState("open");
						this.socket.onopen = void 0;
					}
					onError(error) {
						this.emit("error", {
							type: "WebSocketError",
							error
						});
						this.timeline.error(this.buildTimelineMessage({ error: error.toString() }));
					}
					onClose(closeEvent) {
						if (closeEvent) this.changeState("closed", {
							code: closeEvent.code,
							reason: closeEvent.reason,
							wasClean: closeEvent.wasClean
						});
						else this.changeState("closed");
						this.unbindListeners();
						this.socket = void 0;
					}
					onMessage(message) {
						this.emit("message", message);
					}
					onActivity() {
						this.emit("activity");
					}
					bindListeners() {
						this.socket.onopen = () => {
							this.onOpen();
						};
						this.socket.onerror = (error) => {
							this.onError(error);
						};
						this.socket.onclose = (closeEvent) => {
							this.onClose(closeEvent);
						};
						this.socket.onmessage = (message) => {
							this.onMessage(message);
						};
						if (this.supportsPing()) this.socket.onactivity = () => {
							this.onActivity();
						};
					}
					unbindListeners() {
						if (this.socket) {
							this.socket.onopen = void 0;
							this.socket.onerror = void 0;
							this.socket.onclose = void 0;
							this.socket.onmessage = void 0;
							if (this.supportsPing()) this.socket.onactivity = void 0;
						}
					}
					changeState(state$1, params) {
						this.state = state$1;
						this.timeline.info(this.buildTimelineMessage({
							state: state$1,
							params
						}));
						this.emit(state$1, params);
					}
					buildTimelineMessage(message) {
						return extend$1({ cid: this.id }, message);
					}
				}
				class transport_Transport {
					constructor(hooks) {
						this.hooks = hooks;
					}
					isSupported(environment) {
						return this.hooks.isSupported(environment);
					}
					createConnection(name, priority, key, options) {
						return new transport_connection_TransportConnection(this.hooks, name, priority, key, options);
					}
				}
				var WSTransport = new transport_Transport({
					urls: ws,
					handlesActivityChecks: false,
					supportsPing: false,
					isInitialized: function() {
						return Boolean(runtime.getWebSocketAPI());
					},
					isSupported: function() {
						return Boolean(runtime.getWebSocketAPI());
					},
					getSocket: function(url) {
						return runtime.createWebSocket(url);
					}
				});
				var httpConfiguration = {
					urls: http,
					handlesActivityChecks: false,
					supportsPing: true,
					isInitialized: function() {
						return true;
					}
				};
				var streamingConfiguration = extend$1({ getSocket: function(url) {
					return runtime.HTTPFactory.createStreamingSocket(url);
				} }, httpConfiguration);
				var pollingConfiguration = extend$1({ getSocket: function(url) {
					return runtime.HTTPFactory.createPollingSocket(url);
				} }, httpConfiguration);
				var xhrConfiguration = { isSupported: function() {
					return runtime.isXHRSupported();
				} };
				var transports = {
					ws: WSTransport,
					xhr_streaming: new transport_Transport(extend$1({}, streamingConfiguration, xhrConfiguration)),
					xhr_polling: new transport_Transport(extend$1({}, pollingConfiguration, xhrConfiguration))
				};
				var SockJSTransport = new transport_Transport({
					file: "sockjs",
					urls: sockjs,
					handlesActivityChecks: true,
					supportsPing: false,
					isSupported: function() {
						return true;
					},
					isInitialized: function() {
						return window.SockJS !== void 0;
					},
					getSocket: function(url, options) {
						return new window.SockJS(url, null, {
							js_path: Dependencies.getPath("sockjs", { useTLS: options.useTLS }),
							ignore_null_origin: options.ignoreNullOrigin
						});
					},
					beforeOpen: function(socket, path) {
						socket.send(JSON.stringify({ path }));
					}
				});
				var xdrConfiguration = { isSupported: function(environment) {
					return runtime.isXDRSupported(environment.useTLS);
				} };
				var XDRStreamingTransport = new transport_Transport(extend$1({}, streamingConfiguration, xdrConfiguration));
				var XDRPollingTransport = new transport_Transport(extend$1({}, pollingConfiguration, xdrConfiguration));
				transports.xdr_streaming = XDRStreamingTransport;
				transports.xdr_polling = XDRPollingTransport;
				transports.sockjs = SockJSTransport;
				var transports_transports = transports;
				class net_info_NetInfo extends dispatcher_Dispatcher {
					constructor() {
						super();
						var self$1 = this;
						if (window.addEventListener !== void 0) {
							window.addEventListener("online", function() {
								self$1.emit("online");
							}, false);
							window.addEventListener("offline", function() {
								self$1.emit("offline");
							}, false);
						}
					}
					isOnline() {
						if (window.navigator.onLine === void 0) return true;
						else return window.navigator.onLine;
					}
				}
				var net_info_Network = new net_info_NetInfo();
				class assistant_to_the_transport_manager_AssistantToTheTransportManager {
					constructor(manager, transport, options) {
						this.manager = manager;
						this.transport = transport;
						this.minPingDelay = options.minPingDelay;
						this.maxPingDelay = options.maxPingDelay;
						this.pingDelay = void 0;
					}
					createConnection(name, priority, key, options) {
						options = extend$1({}, options, { activityTimeout: this.pingDelay });
						var connection = this.transport.createConnection(name, priority, key, options);
						var openTimestamp = null;
						var onOpen = function() {
							connection.unbind("open", onOpen);
							connection.bind("closed", onClosed);
							openTimestamp = util.now();
						};
						var onClosed = (closeEvent) => {
							connection.unbind("closed", onClosed);
							if (closeEvent.code === 1002 || closeEvent.code === 1003) this.manager.reportDeath();
							else if (!closeEvent.wasClean && openTimestamp) {
								var lifespan = util.now() - openTimestamp;
								if (lifespan < 2 * this.maxPingDelay) {
									this.manager.reportDeath();
									this.pingDelay = Math.max(lifespan / 2, this.minPingDelay);
								}
							}
						};
						connection.bind("open", onOpen);
						return connection;
					}
					isSupported(environment) {
						return this.manager.isAlive() && this.transport.isSupported(environment);
					}
				}
				const Protocol = {
					decodeMessage: function(messageEvent) {
						try {
							var messageData = JSON.parse(messageEvent.data);
							var pusherEventData = messageData.data;
							if (typeof pusherEventData === "string") try {
								pusherEventData = JSON.parse(messageData.data);
							} catch (e) {}
							var pusherEvent = {
								event: messageData.event,
								channel: messageData.channel,
								data: pusherEventData
							};
							if (messageData.user_id) pusherEvent.user_id = messageData.user_id;
							return pusherEvent;
						} catch (e) {
							throw {
								type: "MessageParseError",
								error: e,
								data: messageEvent.data
							};
						}
					},
					encodeMessage: function(event) {
						return JSON.stringify(event);
					},
					processHandshake: function(messageEvent) {
						var message = Protocol.decodeMessage(messageEvent);
						if (message.event === "pusher:connection_established") {
							if (!message.data.activity_timeout) throw "No activity timeout specified in handshake";
							return {
								action: "connected",
								id: message.data.socket_id,
								activityTimeout: message.data.activity_timeout * 1e3
							};
						} else if (message.event === "pusher:error") return {
							action: this.getCloseAction(message.data),
							error: this.getCloseError(message.data)
						};
						else throw "Invalid handshake";
					},
					getCloseAction: function(closeEvent) {
						if (closeEvent.code < 4e3) if (closeEvent.code >= 1002 && closeEvent.code <= 1004) return "backoff";
						else return null;
						else if (closeEvent.code === 4e3) return "tls_only";
						else if (closeEvent.code < 4100) return "refused";
						else if (closeEvent.code < 4200) return "backoff";
						else if (closeEvent.code < 4300) return "retry";
						else return "refused";
					},
					getCloseError: function(closeEvent) {
						if (closeEvent.code !== 1e3 && closeEvent.code !== 1001) return {
							type: "PusherError",
							data: {
								code: closeEvent.code,
								message: closeEvent.reason || closeEvent.message
							}
						};
						else return null;
					}
				};
				var protocol_protocol = Protocol;
				class connection_Connection extends dispatcher_Dispatcher {
					constructor(id, transport) {
						super();
						this.id = id;
						this.transport = transport;
						this.activityTimeout = transport.activityTimeout;
						this.bindListeners();
					}
					handlesActivityChecks() {
						return this.transport.handlesActivityChecks();
					}
					send(data) {
						return this.transport.send(data);
					}
					send_event(name, data, channel) {
						var event = {
							event: name,
							data
						};
						if (channel) event.channel = channel;
						logger.debug("Event sent", event);
						return this.send(protocol_protocol.encodeMessage(event));
					}
					ping() {
						if (this.transport.supportsPing()) this.transport.ping();
						else this.send_event("pusher:ping", {});
					}
					close() {
						this.transport.close();
					}
					bindListeners() {
						var listeners = {
							message: (messageEvent) => {
								var pusherEvent;
								try {
									pusherEvent = protocol_protocol.decodeMessage(messageEvent);
								} catch (e) {
									this.emit("error", {
										type: "MessageParseError",
										error: e,
										data: messageEvent.data
									});
								}
								if (pusherEvent !== void 0) {
									logger.debug("Event recd", pusherEvent);
									switch (pusherEvent.event) {
										case "pusher:error":
											this.emit("error", {
												type: "PusherError",
												data: pusherEvent.data
											});
											break;
										case "pusher:ping":
											this.emit("ping");
											break;
										case "pusher:pong":
											this.emit("pong");
											break;
									}
									this.emit("message", pusherEvent);
								}
							},
							activity: () => {
								this.emit("activity");
							},
							error: (error) => {
								this.emit("error", error);
							},
							closed: (closeEvent) => {
								unbindListeners();
								if (closeEvent && closeEvent.code) this.handleCloseEvent(closeEvent);
								this.transport = null;
								this.emit("closed");
							}
						};
						var unbindListeners = () => {
							objectApply(listeners, (listener, event) => {
								this.transport.unbind(event, listener);
							});
						};
						objectApply(listeners, (listener, event) => {
							this.transport.bind(event, listener);
						});
					}
					handleCloseEvent(closeEvent) {
						var action = protocol_protocol.getCloseAction(closeEvent);
						var error = protocol_protocol.getCloseError(closeEvent);
						if (error) this.emit("error", error);
						if (action) this.emit(action, {
							action,
							error
						});
					}
				}
				class handshake_Handshake {
					constructor(transport, callback) {
						this.transport = transport;
						this.callback = callback;
						this.bindListeners();
					}
					close() {
						this.unbindListeners();
						this.transport.close();
					}
					bindListeners() {
						this.onMessage = (m) => {
							this.unbindListeners();
							var result;
							try {
								result = protocol_protocol.processHandshake(m);
							} catch (e) {
								this.finish("error", { error: e });
								this.transport.close();
								return;
							}
							if (result.action === "connected") this.finish("connected", {
								connection: new connection_Connection(result.id, this.transport),
								activityTimeout: result.activityTimeout
							});
							else {
								this.finish(result.action, { error: result.error });
								this.transport.close();
							}
						};
						this.onClosed = (closeEvent) => {
							this.unbindListeners();
							var action = protocol_protocol.getCloseAction(closeEvent) || "backoff";
							var error = protocol_protocol.getCloseError(closeEvent);
							this.finish(action, { error });
						};
						this.transport.bind("message", this.onMessage);
						this.transport.bind("closed", this.onClosed);
					}
					unbindListeners() {
						this.transport.unbind("message", this.onMessage);
						this.transport.unbind("closed", this.onClosed);
					}
					finish(action, params) {
						this.callback(extend$1({
							transport: this.transport,
							action
						}, params));
					}
				}
				class timeline_sender_TimelineSender {
					constructor(timeline, options) {
						this.timeline = timeline;
						this.options = options || {};
					}
					send(useTLS, callback) {
						if (this.timeline.isEmpty()) return;
						this.timeline.send(runtime.TimelineTransport.getAgent(this, useTLS), callback);
					}
				}
				class channel_Channel extends dispatcher_Dispatcher {
					constructor(name, pusher) {
						super(function(event, data) {
							logger.debug("No callbacks on " + name + " for " + event);
						});
						this.name = name;
						this.pusher = pusher;
						this.subscribed = false;
						this.subscriptionPending = false;
						this.subscriptionCancelled = false;
					}
					authorize(socketId, callback) {
						return callback(null, { auth: "" });
					}
					trigger(event, data) {
						if (event.indexOf("client-") !== 0) throw new BadEventName("Event '" + event + "' does not start with 'client-'");
						if (!this.subscribed) {
							var suffix = url_store.buildLogSuffix("triggeringClientEvents");
							logger.warn(`Client event triggered before channel 'subscription_succeeded' event . ${suffix}`);
						}
						return this.pusher.send_event(event, data, this.name);
					}
					disconnect() {
						this.subscribed = false;
						this.subscriptionPending = false;
					}
					handleEvent(event) {
						var eventName = event.event;
						var data = event.data;
						if (eventName === "pusher_internal:subscription_succeeded") this.handleSubscriptionSucceededEvent(event);
						else if (eventName === "pusher_internal:subscription_count") this.handleSubscriptionCountEvent(event);
						else if (eventName.indexOf("pusher_internal:") !== 0) this.emit(eventName, data, {});
					}
					handleSubscriptionSucceededEvent(event) {
						this.subscriptionPending = false;
						this.subscribed = true;
						if (this.subscriptionCancelled) this.pusher.unsubscribe(this.name);
						else this.emit("pusher:subscription_succeeded", event.data);
					}
					handleSubscriptionCountEvent(event) {
						if (event.data.subscription_count) this.subscriptionCount = event.data.subscription_count;
						this.emit("pusher:subscription_count", event.data);
					}
					subscribe() {
						if (this.subscribed) return;
						this.subscriptionPending = true;
						this.subscriptionCancelled = false;
						this.authorize(this.pusher.connection.socket_id, (error, data) => {
							if (error) {
								this.subscriptionPending = false;
								logger.error(error.toString());
								this.emit("pusher:subscription_error", Object.assign({}, {
									type: "AuthError",
									error: error.message
								}, error instanceof HTTPAuthError ? { status: error.status } : {}));
							} else this.pusher.send_event("pusher:subscribe", {
								auth: data.auth,
								channel_data: data.channel_data,
								channel: this.name
							});
						});
					}
					unsubscribe() {
						this.subscribed = false;
						this.pusher.send_event("pusher:unsubscribe", { channel: this.name });
					}
					cancelSubscription() {
						this.subscriptionCancelled = true;
					}
					reinstateSubscription() {
						this.subscriptionCancelled = false;
					}
				}
				class private_channel_PrivateChannel extends channel_Channel {
					authorize(socketId, callback) {
						return this.pusher.config.channelAuthorizer({
							channelName: this.name,
							socketId
						}, callback);
					}
				}
				class members_Members {
					constructor() {
						this.reset();
					}
					get(id) {
						if (Object.prototype.hasOwnProperty.call(this.members, id)) return {
							id,
							info: this.members[id]
						};
						else return null;
					}
					each(callback) {
						objectApply(this.members, (member, id) => {
							callback(this.get(id));
						});
					}
					setMyID(id) {
						this.myID = id;
					}
					onSubscription(subscriptionData) {
						this.members = subscriptionData.presence.hash;
						this.count = subscriptionData.presence.count;
						this.me = this.get(this.myID);
					}
					addMember(memberData) {
						if (this.get(memberData.user_id) === null) this.count++;
						this.members[memberData.user_id] = memberData.user_info;
						return this.get(memberData.user_id);
					}
					removeMember(memberData) {
						var member = this.get(memberData.user_id);
						if (member) {
							delete this.members[memberData.user_id];
							this.count--;
						}
						return member;
					}
					reset() {
						this.members = {};
						this.count = 0;
						this.myID = null;
						this.me = null;
					}
				}
				var __awaiter = function(thisArg, _arguments, P, generator) {
					function adopt(value) {
						return value instanceof P ? value : new P(function(resolve) {
							resolve(value);
						});
					}
					return new (P || (P = Promise))(function(resolve, reject) {
						function fulfilled(value) {
							try {
								step(generator.next(value));
							} catch (e) {
								reject(e);
							}
						}
						function rejected(value) {
							try {
								step(generator["throw"](value));
							} catch (e) {
								reject(e);
							}
						}
						function step(result) {
							result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected);
						}
						step((generator = generator.apply(thisArg, _arguments || [])).next());
					});
				};
				class presence_channel_PresenceChannel extends private_channel_PrivateChannel {
					constructor(name, pusher) {
						super(name, pusher);
						this.members = new members_Members();
					}
					authorize(socketId, callback) {
						super.authorize(socketId, (error, authData) => __awaiter(this, void 0, void 0, function* () {
							if (!error) {
								authData = authData;
								if (authData.channel_data != null) {
									var channelData = JSON.parse(authData.channel_data);
									this.members.setMyID(channelData.user_id);
								} else {
									yield this.pusher.user.signinDonePromise;
									if (this.pusher.user.user_data != null) this.members.setMyID(this.pusher.user.user_data.id);
									else {
										let suffix = url_store.buildLogSuffix("authorizationEndpoint");
										logger.error(`Invalid auth response for channel '${this.name}', expected 'channel_data' field. ${suffix}, or the user should be signed in.`);
										callback("Invalid auth response");
										return;
									}
								}
							}
							callback(error, authData);
						}));
					}
					handleEvent(event) {
						var eventName = event.event;
						if (eventName.indexOf("pusher_internal:") === 0) this.handleInternalEvent(event);
						else {
							var data = event.data;
							var metadata = {};
							if (event.user_id) metadata.user_id = event.user_id;
							this.emit(eventName, data, metadata);
						}
					}
					handleInternalEvent(event) {
						var eventName = event.event;
						var data = event.data;
						switch (eventName) {
							case "pusher_internal:subscription_succeeded":
								this.handleSubscriptionSucceededEvent(event);
								break;
							case "pusher_internal:subscription_count":
								this.handleSubscriptionCountEvent(event);
								break;
							case "pusher_internal:member_added":
								var addedMember = this.members.addMember(data);
								this.emit("pusher:member_added", addedMember);
								break;
							case "pusher_internal:member_removed":
								var removedMember = this.members.removeMember(data);
								if (removedMember) this.emit("pusher:member_removed", removedMember);
								break;
						}
					}
					handleSubscriptionSucceededEvent(event) {
						this.subscriptionPending = false;
						this.subscribed = true;
						if (this.subscriptionCancelled) this.pusher.unsubscribe(this.name);
						else {
							this.members.onSubscription(event.data);
							this.emit("pusher:subscription_succeeded", this.members);
						}
					}
					disconnect() {
						this.members.reset();
						super.disconnect();
					}
				}
				var utf8 = __webpack_require__(1);
				var base64 = __webpack_require__(0);
				class encrypted_channel_EncryptedChannel extends private_channel_PrivateChannel {
					constructor(name, pusher, nacl) {
						super(name, pusher);
						this.key = null;
						this.nacl = nacl;
					}
					authorize(socketId, callback) {
						super.authorize(socketId, (error, authData) => {
							if (error) {
								callback(error, authData);
								return;
							}
							let sharedSecret = authData["shared_secret"];
							if (!sharedSecret) {
								callback(/* @__PURE__ */ new Error(`No shared_secret key in auth payload for encrypted channel: ${this.name}`), null);
								return;
							}
							this.key = Object(base64["decode"])(sharedSecret);
							delete authData["shared_secret"];
							callback(null, authData);
						});
					}
					trigger(event, data) {
						throw new UnsupportedFeature("Client events are not currently supported for encrypted channels");
					}
					handleEvent(event) {
						var eventName = event.event;
						var data = event.data;
						if (eventName.indexOf("pusher_internal:") === 0 || eventName.indexOf("pusher:") === 0) {
							super.handleEvent(event);
							return;
						}
						this.handleEncryptedEvent(eventName, data);
					}
					handleEncryptedEvent(event, data) {
						if (!this.key) {
							logger.debug("Received encrypted event before key has been retrieved from the authEndpoint");
							return;
						}
						if (!data.ciphertext || !data.nonce) {
							logger.error("Unexpected format for encrypted event, expected object with `ciphertext` and `nonce` fields, got: " + data);
							return;
						}
						let cipherText = Object(base64["decode"])(data.ciphertext);
						if (cipherText.length < this.nacl.secretbox.overheadLength) {
							logger.error(`Expected encrypted event ciphertext length to be ${this.nacl.secretbox.overheadLength}, got: ${cipherText.length}`);
							return;
						}
						let nonce = Object(base64["decode"])(data.nonce);
						if (nonce.length < this.nacl.secretbox.nonceLength) {
							logger.error(`Expected encrypted event nonce length to be ${this.nacl.secretbox.nonceLength}, got: ${nonce.length}`);
							return;
						}
						let bytes = this.nacl.secretbox.open(cipherText, nonce, this.key);
						if (bytes === null) {
							logger.debug("Failed to decrypt an event, probably because it was encrypted with a different key. Fetching a new key from the authEndpoint...");
							this.authorize(this.pusher.connection.socket_id, (error, authData) => {
								if (error) {
									logger.error(`Failed to make a request to the authEndpoint: ${authData}. Unable to fetch new key, so dropping encrypted event`);
									return;
								}
								bytes = this.nacl.secretbox.open(cipherText, nonce, this.key);
								if (bytes === null) {
									logger.error(`Failed to decrypt event with new key. Dropping encrypted event`);
									return;
								}
								this.emit(event, this.getDataToEmit(bytes));
							});
							return;
						}
						this.emit(event, this.getDataToEmit(bytes));
					}
					getDataToEmit(bytes) {
						let raw = Object(utf8["decode"])(bytes);
						try {
							return JSON.parse(raw);
						} catch (_a) {
							return raw;
						}
					}
				}
				class connection_manager_ConnectionManager extends dispatcher_Dispatcher {
					constructor(key, options) {
						super();
						this.state = "initialized";
						this.connection = null;
						this.key = key;
						this.options = options;
						this.timeline = this.options.timeline;
						this.usingTLS = this.options.useTLS;
						this.errorCallbacks = this.buildErrorCallbacks();
						this.connectionCallbacks = this.buildConnectionCallbacks(this.errorCallbacks);
						this.handshakeCallbacks = this.buildHandshakeCallbacks(this.errorCallbacks);
						var Network = runtime.getNetwork();
						Network.bind("online", () => {
							this.timeline.info({ netinfo: "online" });
							if (this.state === "connecting" || this.state === "unavailable") this.retryIn(0);
						});
						Network.bind("offline", () => {
							this.timeline.info({ netinfo: "offline" });
							if (this.connection) this.sendActivityCheck();
						});
						this.updateStrategy();
					}
					connect() {
						if (this.connection || this.runner) return;
						if (!this.strategy.isSupported()) {
							this.updateState("failed");
							return;
						}
						this.updateState("connecting");
						this.startConnecting();
						this.setUnavailableTimer();
					}
					send(data) {
						if (this.connection) return this.connection.send(data);
						else return false;
					}
					send_event(name, data, channel) {
						if (this.connection) return this.connection.send_event(name, data, channel);
						else return false;
					}
					disconnect() {
						this.disconnectInternally();
						this.updateState("disconnected");
					}
					isUsingTLS() {
						return this.usingTLS;
					}
					startConnecting() {
						var callback = (error, handshake) => {
							if (error) this.runner = this.strategy.connect(0, callback);
							else if (handshake.action === "error") {
								this.emit("error", {
									type: "HandshakeError",
									error: handshake.error
								});
								this.timeline.error({ handshakeError: handshake.error });
							} else {
								this.abortConnecting();
								this.handshakeCallbacks[handshake.action](handshake);
							}
						};
						this.runner = this.strategy.connect(0, callback);
					}
					abortConnecting() {
						if (this.runner) {
							this.runner.abort();
							this.runner = null;
						}
					}
					disconnectInternally() {
						this.abortConnecting();
						this.clearRetryTimer();
						this.clearUnavailableTimer();
						if (this.connection) this.abandonConnection().close();
					}
					updateStrategy() {
						this.strategy = this.options.getStrategy({
							key: this.key,
							timeline: this.timeline,
							useTLS: this.usingTLS
						});
					}
					retryIn(delay) {
						this.timeline.info({
							action: "retry",
							delay
						});
						if (delay > 0) this.emit("connecting_in", Math.round(delay / 1e3));
						this.retryTimer = new timers_OneOffTimer(delay || 0, () => {
							this.disconnectInternally();
							this.connect();
						});
					}
					clearRetryTimer() {
						if (this.retryTimer) {
							this.retryTimer.ensureAborted();
							this.retryTimer = null;
						}
					}
					setUnavailableTimer() {
						this.unavailableTimer = new timers_OneOffTimer(this.options.unavailableTimeout, () => {
							this.updateState("unavailable");
						});
					}
					clearUnavailableTimer() {
						if (this.unavailableTimer) this.unavailableTimer.ensureAborted();
					}
					sendActivityCheck() {
						this.stopActivityCheck();
						this.connection.ping();
						this.activityTimer = new timers_OneOffTimer(this.options.pongTimeout, () => {
							this.timeline.error({ pong_timed_out: this.options.pongTimeout });
							this.retryIn(0);
						});
					}
					resetActivityCheck() {
						this.stopActivityCheck();
						if (this.connection && !this.connection.handlesActivityChecks()) this.activityTimer = new timers_OneOffTimer(this.activityTimeout, () => {
							this.sendActivityCheck();
						});
					}
					stopActivityCheck() {
						if (this.activityTimer) this.activityTimer.ensureAborted();
					}
					buildConnectionCallbacks(errorCallbacks) {
						return extend$1({}, errorCallbacks, {
							message: (message) => {
								this.resetActivityCheck();
								this.emit("message", message);
							},
							ping: () => {
								this.send_event("pusher:pong", {});
							},
							activity: () => {
								this.resetActivityCheck();
							},
							error: (error) => {
								this.emit("error", error);
							},
							closed: () => {
								this.abandonConnection();
								if (this.shouldRetry()) this.retryIn(1e3);
							}
						});
					}
					buildHandshakeCallbacks(errorCallbacks) {
						return extend$1({}, errorCallbacks, { connected: (handshake) => {
							this.activityTimeout = Math.min(this.options.activityTimeout, handshake.activityTimeout, handshake.connection.activityTimeout || Infinity);
							this.clearUnavailableTimer();
							this.setConnection(handshake.connection);
							this.socket_id = this.connection.id;
							this.updateState("connected", { socket_id: this.socket_id });
						} });
					}
					buildErrorCallbacks() {
						let withErrorEmitted = (callback) => {
							return (result) => {
								if (result.error) this.emit("error", {
									type: "WebSocketError",
									error: result.error
								});
								callback(result);
							};
						};
						return {
							tls_only: withErrorEmitted(() => {
								this.usingTLS = true;
								this.updateStrategy();
								this.retryIn(0);
							}),
							refused: withErrorEmitted(() => {
								this.disconnect();
							}),
							backoff: withErrorEmitted(() => {
								this.retryIn(1e3);
							}),
							retry: withErrorEmitted(() => {
								this.retryIn(0);
							})
						};
					}
					setConnection(connection) {
						this.connection = connection;
						for (var event in this.connectionCallbacks) this.connection.bind(event, this.connectionCallbacks[event]);
						this.resetActivityCheck();
					}
					abandonConnection() {
						if (!this.connection) return;
						this.stopActivityCheck();
						for (var event in this.connectionCallbacks) this.connection.unbind(event, this.connectionCallbacks[event]);
						var connection = this.connection;
						this.connection = null;
						return connection;
					}
					updateState(newState, data) {
						var previousState = this.state;
						this.state = newState;
						if (previousState !== newState) {
							var newStateDescription = newState;
							if (newStateDescription === "connected") newStateDescription += " with new socket ID " + data.socket_id;
							logger.debug("State changed", previousState + " -> " + newStateDescription);
							this.timeline.info({
								state: newState,
								params: data
							});
							this.emit("state_change", {
								previous: previousState,
								current: newState
							});
							this.emit(newState, data);
						}
					}
					shouldRetry() {
						return this.state === "connecting" || this.state === "connected";
					}
				}
				class channels_Channels {
					constructor() {
						this.channels = {};
					}
					add(name, pusher) {
						if (!this.channels[name]) this.channels[name] = createChannel(name, pusher);
						return this.channels[name];
					}
					all() {
						return values(this.channels);
					}
					find(name) {
						return this.channels[name];
					}
					remove(name) {
						var channel = this.channels[name];
						delete this.channels[name];
						return channel;
					}
					disconnect() {
						objectApply(this.channels, function(channel) {
							channel.disconnect();
						});
					}
				}
				function createChannel(name, pusher) {
					if (name.indexOf("private-encrypted-") === 0) {
						if (pusher.config.nacl) return factory$1.createEncryptedChannel(name, pusher, pusher.config.nacl);
						throw new UnsupportedFeature(`Tried to subscribe to a private-encrypted- channel but no nacl implementation available. ${url_store.buildLogSuffix("encryptedChannelSupport")}`);
					} else if (name.indexOf("private-") === 0) return factory$1.createPrivateChannel(name, pusher);
					else if (name.indexOf("presence-") === 0) return factory$1.createPresenceChannel(name, pusher);
					else if (name.indexOf("#") === 0) throw new BadChannelName("Cannot create a channel with name \"" + name + "\".");
					else return factory$1.createChannel(name, pusher);
				}
				var factory$1 = {
					createChannels() {
						return new channels_Channels();
					},
					createConnectionManager(key, options) {
						return new connection_manager_ConnectionManager(key, options);
					},
					createChannel(name, pusher) {
						return new channel_Channel(name, pusher);
					},
					createPrivateChannel(name, pusher) {
						return new private_channel_PrivateChannel(name, pusher);
					},
					createPresenceChannel(name, pusher) {
						return new presence_channel_PresenceChannel(name, pusher);
					},
					createEncryptedChannel(name, pusher, nacl) {
						return new encrypted_channel_EncryptedChannel(name, pusher, nacl);
					},
					createTimelineSender(timeline, options) {
						return new timeline_sender_TimelineSender(timeline, options);
					},
					createHandshake(transport, callback) {
						return new handshake_Handshake(transport, callback);
					},
					createAssistantToTheTransportManager(manager, transport, options) {
						return new assistant_to_the_transport_manager_AssistantToTheTransportManager(manager, transport, options);
					}
				};
				class transport_manager_TransportManager {
					constructor(options) {
						this.options = options || {};
						this.livesLeft = this.options.lives || Infinity;
					}
					getAssistant(transport) {
						return factory$1.createAssistantToTheTransportManager(this, transport, {
							minPingDelay: this.options.minPingDelay,
							maxPingDelay: this.options.maxPingDelay
						});
					}
					isAlive() {
						return this.livesLeft > 0;
					}
					reportDeath() {
						this.livesLeft -= 1;
					}
				}
				class sequential_strategy_SequentialStrategy {
					constructor(strategies, options) {
						this.strategies = strategies;
						this.loop = Boolean(options.loop);
						this.failFast = Boolean(options.failFast);
						this.timeout = options.timeout;
						this.timeoutLimit = options.timeoutLimit;
					}
					isSupported() {
						return any(this.strategies, util.method("isSupported"));
					}
					connect(minPriority, callback) {
						var strategies = this.strategies;
						var current = 0;
						var timeout = this.timeout;
						var runner = null;
						var tryNextStrategy = (error, handshake) => {
							if (handshake) callback(null, handshake);
							else {
								current = current + 1;
								if (this.loop) current = current % strategies.length;
								if (current < strategies.length) {
									if (timeout) {
										timeout = timeout * 2;
										if (this.timeoutLimit) timeout = Math.min(timeout, this.timeoutLimit);
									}
									runner = this.tryStrategy(strategies[current], minPriority, {
										timeout,
										failFast: this.failFast
									}, tryNextStrategy);
								} else callback(true);
							}
						};
						runner = this.tryStrategy(strategies[current], minPriority, {
							timeout,
							failFast: this.failFast
						}, tryNextStrategy);
						return {
							abort: function() {
								runner.abort();
							},
							forceMinPriority: function(p) {
								minPriority = p;
								if (runner) runner.forceMinPriority(p);
							}
						};
					}
					tryStrategy(strategy, minPriority, options, callback) {
						var timer = null;
						var runner = null;
						if (options.timeout > 0) timer = new timers_OneOffTimer(options.timeout, function() {
							runner.abort();
							callback(true);
						});
						runner = strategy.connect(minPriority, function(error, handshake) {
							if (error && timer && timer.isRunning() && !options.failFast) return;
							if (timer) timer.ensureAborted();
							callback(error, handshake);
						});
						return {
							abort: function() {
								if (timer) timer.ensureAborted();
								runner.abort();
							},
							forceMinPriority: function(p) {
								runner.forceMinPriority(p);
							}
						};
					}
				}
				class best_connected_ever_strategy_BestConnectedEverStrategy {
					constructor(strategies) {
						this.strategies = strategies;
					}
					isSupported() {
						return any(this.strategies, util.method("isSupported"));
					}
					connect(minPriority, callback) {
						return connect(this.strategies, minPriority, function(i, runners) {
							return function(error, handshake) {
								runners[i].error = error;
								if (error) {
									if (allRunnersFailed(runners)) callback(true);
									return;
								}
								apply(runners, function(runner) {
									runner.forceMinPriority(handshake.transport.priority);
								});
								callback(null, handshake);
							};
						});
					}
				}
				function connect(strategies, minPriority, callbackBuilder) {
					var runners = map(strategies, function(strategy, i, _, rs) {
						return strategy.connect(minPriority, callbackBuilder(i, rs));
					});
					return {
						abort: function() {
							apply(runners, abortRunner);
						},
						forceMinPriority: function(p) {
							apply(runners, function(runner) {
								runner.forceMinPriority(p);
							});
						}
					};
				}
				function allRunnersFailed(runners) {
					return collections_all(runners, function(runner) {
						return Boolean(runner.error);
					});
				}
				function abortRunner(runner) {
					if (!runner.error && !runner.aborted) {
						runner.abort();
						runner.aborted = true;
					}
				}
				class websocket_prioritized_cached_strategy_WebSocketPrioritizedCachedStrategy {
					constructor(strategy, transports$1, options) {
						this.strategy = strategy;
						this.transports = transports$1;
						this.ttl = options.ttl || 1800 * 1e3;
						this.usingTLS = options.useTLS;
						this.timeline = options.timeline;
					}
					isSupported() {
						return this.strategy.isSupported();
					}
					connect(minPriority, callback) {
						var usingTLS = this.usingTLS;
						var info = fetchTransportCache(usingTLS);
						var cacheSkipCount = info && info.cacheSkipCount ? info.cacheSkipCount : 0;
						var strategies = [this.strategy];
						if (info && info.timestamp + this.ttl >= util.now()) {
							var transport = this.transports[info.transport];
							if (transport) if (["ws", "wss"].includes(info.transport) || cacheSkipCount > 3) {
								this.timeline.info({
									cached: true,
									transport: info.transport,
									latency: info.latency
								});
								strategies.push(new sequential_strategy_SequentialStrategy([transport], {
									timeout: info.latency * 2 + 1e3,
									failFast: true
								}));
							} else cacheSkipCount++;
						}
						var startTimestamp = util.now();
						var runner = strategies.pop().connect(minPriority, function cb(error, handshake) {
							if (error) {
								flushTransportCache(usingTLS);
								if (strategies.length > 0) {
									startTimestamp = util.now();
									runner = strategies.pop().connect(minPriority, cb);
								} else callback(error);
							} else {
								storeTransportCache(usingTLS, handshake.transport.name, util.now() - startTimestamp, cacheSkipCount);
								callback(null, handshake);
							}
						});
						return {
							abort: function() {
								runner.abort();
							},
							forceMinPriority: function(p) {
								minPriority = p;
								if (runner) runner.forceMinPriority(p);
							}
						};
					}
				}
				function getTransportCacheKey(usingTLS) {
					return "pusherTransport" + (usingTLS ? "TLS" : "NonTLS");
				}
				function fetchTransportCache(usingTLS) {
					var storage = runtime.getLocalStorage();
					if (storage) try {
						var serializedCache = storage[getTransportCacheKey(usingTLS)];
						if (serializedCache) return JSON.parse(serializedCache);
					} catch (e) {
						flushTransportCache(usingTLS);
					}
					return null;
				}
				function storeTransportCache(usingTLS, transport, latency, cacheSkipCount) {
					var storage = runtime.getLocalStorage();
					if (storage) try {
						storage[getTransportCacheKey(usingTLS)] = safeJSONStringify({
							timestamp: util.now(),
							transport,
							latency,
							cacheSkipCount
						});
					} catch (e) {}
				}
				function flushTransportCache(usingTLS) {
					var storage = runtime.getLocalStorage();
					if (storage) try {
						delete storage[getTransportCacheKey(usingTLS)];
					} catch (e) {}
				}
				class delayed_strategy_DelayedStrategy {
					constructor(strategy, { delay: number }) {
						this.strategy = strategy;
						this.options = { delay: number };
					}
					isSupported() {
						return this.strategy.isSupported();
					}
					connect(minPriority, callback) {
						var strategy = this.strategy;
						var runner;
						var timer = new timers_OneOffTimer(this.options.delay, function() {
							runner = strategy.connect(minPriority, callback);
						});
						return {
							abort: function() {
								timer.ensureAborted();
								if (runner) runner.abort();
							},
							forceMinPriority: function(p) {
								minPriority = p;
								if (runner) runner.forceMinPriority(p);
							}
						};
					}
				}
				class IfStrategy {
					constructor(test$1, trueBranch, falseBranch) {
						this.test = test$1;
						this.trueBranch = trueBranch;
						this.falseBranch = falseBranch;
					}
					isSupported() {
						return (this.test() ? this.trueBranch : this.falseBranch).isSupported();
					}
					connect(minPriority, callback) {
						return (this.test() ? this.trueBranch : this.falseBranch).connect(minPriority, callback);
					}
				}
				class FirstConnectedStrategy {
					constructor(strategy) {
						this.strategy = strategy;
					}
					isSupported() {
						return this.strategy.isSupported();
					}
					connect(minPriority, callback) {
						var runner = this.strategy.connect(minPriority, function(error, handshake) {
							if (handshake) runner.abort();
							callback(error, handshake);
						});
						return runner;
					}
				}
				function testSupportsStrategy(strategy) {
					return function() {
						return strategy.isSupported();
					};
				}
				var getDefaultStrategy = function(config, baseOptions, defineTransport) {
					var definedTransports = {};
					function defineTransportStrategy(name, type, priority, options, manager) {
						var transport = defineTransport(config, name, type, priority, options, manager);
						definedTransports[name] = transport;
						return transport;
					}
					var ws_options = Object.assign({}, baseOptions, {
						hostNonTLS: config.wsHost + ":" + config.wsPort,
						hostTLS: config.wsHost + ":" + config.wssPort,
						httpPath: config.wsPath
					});
					var wss_options = Object.assign({}, ws_options, { useTLS: true });
					var sockjs_options = Object.assign({}, baseOptions, {
						hostNonTLS: config.httpHost + ":" + config.httpPort,
						hostTLS: config.httpHost + ":" + config.httpsPort,
						httpPath: config.httpPath
					});
					var timeouts = {
						loop: true,
						timeout: 15e3,
						timeoutLimit: 6e4
					};
					var ws_manager = new transport_manager_TransportManager({
						minPingDelay: 1e4,
						maxPingDelay: config.activityTimeout
					});
					var streaming_manager = new transport_manager_TransportManager({
						lives: 2,
						minPingDelay: 1e4,
						maxPingDelay: config.activityTimeout
					});
					var ws_transport = defineTransportStrategy("ws", "ws", 3, ws_options, ws_manager);
					var wss_transport = defineTransportStrategy("wss", "ws", 3, wss_options, ws_manager);
					var sockjs_transport = defineTransportStrategy("sockjs", "sockjs", 1, sockjs_options);
					var xhr_streaming_transport = defineTransportStrategy("xhr_streaming", "xhr_streaming", 1, sockjs_options, streaming_manager);
					var xdr_streaming_transport = defineTransportStrategy("xdr_streaming", "xdr_streaming", 1, sockjs_options, streaming_manager);
					var xhr_polling_transport = defineTransportStrategy("xhr_polling", "xhr_polling", 1, sockjs_options);
					var xdr_polling_transport = defineTransportStrategy("xdr_polling", "xdr_polling", 1, sockjs_options);
					var ws_loop = new sequential_strategy_SequentialStrategy([ws_transport], timeouts);
					var wss_loop = new sequential_strategy_SequentialStrategy([wss_transport], timeouts);
					var sockjs_loop = new sequential_strategy_SequentialStrategy([sockjs_transport], timeouts);
					var streaming_loop = new sequential_strategy_SequentialStrategy([new IfStrategy(testSupportsStrategy(xhr_streaming_transport), xhr_streaming_transport, xdr_streaming_transport)], timeouts);
					var polling_loop = new sequential_strategy_SequentialStrategy([new IfStrategy(testSupportsStrategy(xhr_polling_transport), xhr_polling_transport, xdr_polling_transport)], timeouts);
					var http_loop = new sequential_strategy_SequentialStrategy([new IfStrategy(testSupportsStrategy(streaming_loop), new best_connected_ever_strategy_BestConnectedEverStrategy([streaming_loop, new delayed_strategy_DelayedStrategy(polling_loop, { delay: 4e3 })]), polling_loop)], timeouts);
					var http_fallback_loop = new IfStrategy(testSupportsStrategy(http_loop), http_loop, sockjs_loop);
					var wsStrategy;
					if (baseOptions.useTLS) wsStrategy = new best_connected_ever_strategy_BestConnectedEverStrategy([ws_loop, new delayed_strategy_DelayedStrategy(http_fallback_loop, { delay: 2e3 })]);
					else wsStrategy = new best_connected_ever_strategy_BestConnectedEverStrategy([
						ws_loop,
						new delayed_strategy_DelayedStrategy(wss_loop, { delay: 2e3 }),
						new delayed_strategy_DelayedStrategy(http_fallback_loop, { delay: 5e3 })
					]);
					return new websocket_prioritized_cached_strategy_WebSocketPrioritizedCachedStrategy(new FirstConnectedStrategy(new IfStrategy(testSupportsStrategy(ws_transport), wsStrategy, http_fallback_loop)), definedTransports, {
						ttl: 18e5,
						timeline: baseOptions.timeline,
						useTLS: baseOptions.useTLS
					});
				};
				var default_strategy = getDefaultStrategy;
				var transport_connection_initializer = (function() {
					var self$1 = this;
					self$1.timeline.info(self$1.buildTimelineMessage({ transport: self$1.name + (self$1.options.useTLS ? "s" : "") }));
					if (self$1.hooks.isInitialized()) self$1.changeState("initialized");
					else if (self$1.hooks.file) {
						self$1.changeState("initializing");
						Dependencies.load(self$1.hooks.file, { useTLS: self$1.options.useTLS }, function(error, callback) {
							if (self$1.hooks.isInitialized()) {
								self$1.changeState("initialized");
								callback(true);
							} else {
								if (error) self$1.onError(error);
								self$1.onClose();
								callback(false);
							}
						});
					} else self$1.onClose();
				});
				var http_xdomain_request = {
					getRequest: function(socket) {
						var xdr = new window.XDomainRequest();
						xdr.ontimeout = function() {
							socket.emit("error", new RequestTimedOut());
							socket.close();
						};
						xdr.onerror = function(e) {
							socket.emit("error", e);
							socket.close();
						};
						xdr.onprogress = function() {
							if (xdr.responseText && xdr.responseText.length > 0) socket.onChunk(200, xdr.responseText);
						};
						xdr.onload = function() {
							if (xdr.responseText && xdr.responseText.length > 0) socket.onChunk(200, xdr.responseText);
							socket.emit("finished", 200);
							socket.close();
						};
						return xdr;
					},
					abortRequest: function(xdr) {
						xdr.ontimeout = xdr.onerror = xdr.onprogress = xdr.onload = null;
						xdr.abort();
					}
				};
				const MAX_BUFFER_LENGTH = 256 * 1024;
				class http_request_HTTPRequest extends dispatcher_Dispatcher {
					constructor(hooks, method, url) {
						super();
						this.hooks = hooks;
						this.method = method;
						this.url = url;
					}
					start(payload) {
						this.position = 0;
						this.xhr = this.hooks.getRequest(this);
						this.unloader = () => {
							this.close();
						};
						runtime.addUnloadListener(this.unloader);
						this.xhr.open(this.method, this.url, true);
						if (this.xhr.setRequestHeader) this.xhr.setRequestHeader("Content-Type", "application/json");
						this.xhr.send(payload);
					}
					close() {
						if (this.unloader) {
							runtime.removeUnloadListener(this.unloader);
							this.unloader = null;
						}
						if (this.xhr) {
							this.hooks.abortRequest(this.xhr);
							this.xhr = null;
						}
					}
					onChunk(status, data) {
						while (true) {
							var chunk = this.advanceBuffer(data);
							if (chunk) this.emit("chunk", {
								status,
								data: chunk
							});
							else break;
						}
						if (this.isBufferTooLong(data)) this.emit("buffer_too_long");
					}
					advanceBuffer(buffer) {
						var unreadData = buffer.slice(this.position);
						var endOfLinePosition = unreadData.indexOf("\n");
						if (endOfLinePosition !== -1) {
							this.position += endOfLinePosition + 1;
							return unreadData.slice(0, endOfLinePosition);
						} else return null;
					}
					isBufferTooLong(buffer) {
						return this.position === buffer.length && buffer.length > MAX_BUFFER_LENGTH;
					}
				}
				var State;
				(function(State$1) {
					State$1[State$1["CONNECTING"] = 0] = "CONNECTING";
					State$1[State$1["OPEN"] = 1] = "OPEN";
					State$1[State$1["CLOSED"] = 3] = "CLOSED";
				})(State || (State = {}));
				var state = State;
				var autoIncrement = 1;
				class http_socket_HTTPSocket {
					constructor(hooks, url) {
						this.hooks = hooks;
						this.session = randomNumber(1e3) + "/" + randomString(8);
						this.location = getLocation(url);
						this.readyState = state.CONNECTING;
						this.openStream();
					}
					send(payload) {
						return this.sendRaw(JSON.stringify([payload]));
					}
					ping() {
						this.hooks.sendHeartbeat(this);
					}
					close(code, reason) {
						this.onClose(code, reason, true);
					}
					sendRaw(payload) {
						if (this.readyState === state.OPEN) try {
							runtime.createSocketRequest("POST", getUniqueURL(getSendURL(this.location, this.session))).start(payload);
							return true;
						} catch (e) {
							return false;
						}
						else return false;
					}
					reconnect() {
						this.closeStream();
						this.openStream();
					}
					onClose(code, reason, wasClean) {
						this.closeStream();
						this.readyState = state.CLOSED;
						if (this.onclose) this.onclose({
							code,
							reason,
							wasClean
						});
					}
					onChunk(chunk) {
						if (chunk.status !== 200) return;
						if (this.readyState === state.OPEN) this.onActivity();
						var payload;
						switch (chunk.data.slice(0, 1)) {
							case "o":
								payload = JSON.parse(chunk.data.slice(1) || "{}");
								this.onOpen(payload);
								break;
							case "a":
								payload = JSON.parse(chunk.data.slice(1) || "[]");
								for (var i = 0; i < payload.length; i++) this.onEvent(payload[i]);
								break;
							case "m":
								payload = JSON.parse(chunk.data.slice(1) || "null");
								this.onEvent(payload);
								break;
							case "h":
								this.hooks.onHeartbeat(this);
								break;
							case "c":
								payload = JSON.parse(chunk.data.slice(1) || "[]");
								this.onClose(payload[0], payload[1], true);
								break;
						}
					}
					onOpen(options) {
						if (this.readyState === state.CONNECTING) {
							if (options && options.hostname) this.location.base = replaceHost(this.location.base, options.hostname);
							this.readyState = state.OPEN;
							if (this.onopen) this.onopen();
						} else this.onClose(1006, "Server lost session", true);
					}
					onEvent(event) {
						if (this.readyState === state.OPEN && this.onmessage) this.onmessage({ data: event });
					}
					onActivity() {
						if (this.onactivity) this.onactivity();
					}
					onError(error) {
						if (this.onerror) this.onerror(error);
					}
					openStream() {
						this.stream = runtime.createSocketRequest("POST", getUniqueURL(this.hooks.getReceiveURL(this.location, this.session)));
						this.stream.bind("chunk", (chunk) => {
							this.onChunk(chunk);
						});
						this.stream.bind("finished", (status) => {
							this.hooks.onFinished(this, status);
						});
						this.stream.bind("buffer_too_long", () => {
							this.reconnect();
						});
						try {
							this.stream.start();
						} catch (error) {
							util.defer(() => {
								this.onError(error);
								this.onClose(1006, "Could not start streaming", false);
							});
						}
					}
					closeStream() {
						if (this.stream) {
							this.stream.unbind_all();
							this.stream.close();
							this.stream = null;
						}
					}
				}
				function getLocation(url) {
					var parts = /([^\?]*)\/*(\??.*)/.exec(url);
					return {
						base: parts[1],
						queryString: parts[2]
					};
				}
				function getSendURL(url, session) {
					return url.base + "/" + session + "/xhr_send";
				}
				function getUniqueURL(url) {
					return url + (url.indexOf("?") === -1 ? "?" : "&") + "t=" + +/* @__PURE__ */ new Date() + "&n=" + autoIncrement++;
				}
				function replaceHost(url, hostname) {
					var urlParts = /(https?:\/\/)([^\/:]+)((\/|:)?.*)/.exec(url);
					return urlParts[1] + hostname + urlParts[3];
				}
				function randomNumber(max) {
					return runtime.randomInt(max);
				}
				function randomString(length) {
					var result = [];
					for (var i = 0; i < length; i++) result.push(randomNumber(32).toString(32));
					return result.join("");
				}
				var http_socket = http_socket_HTTPSocket;
				var http_streaming_socket = {
					getReceiveURL: function(url, session) {
						return url.base + "/" + session + "/xhr_streaming" + url.queryString;
					},
					onHeartbeat: function(socket) {
						socket.sendRaw("[]");
					},
					sendHeartbeat: function(socket) {
						socket.sendRaw("[]");
					},
					onFinished: function(socket, status) {
						socket.onClose(1006, "Connection interrupted (" + status + ")", false);
					}
				};
				var http_polling_socket = {
					getReceiveURL: function(url, session) {
						return url.base + "/" + session + "/xhr" + url.queryString;
					},
					onHeartbeat: function() {},
					sendHeartbeat: function(socket) {
						socket.sendRaw("[]");
					},
					onFinished: function(socket, status) {
						if (status === 200) socket.reconnect();
						else socket.onClose(1006, "Connection interrupted (" + status + ")", false);
					}
				};
				var http_xhr_request = {
					getRequest: function(socket) {
						var xhr = new (runtime.getXHRAPI())();
						xhr.onreadystatechange = xhr.onprogress = function() {
							switch (xhr.readyState) {
								case 3:
									if (xhr.responseText && xhr.responseText.length > 0) socket.onChunk(xhr.status, xhr.responseText);
									break;
								case 4:
									if (xhr.responseText && xhr.responseText.length > 0) socket.onChunk(xhr.status, xhr.responseText);
									socket.emit("finished", xhr.status);
									socket.close();
									break;
							}
						};
						return xhr;
					},
					abortRequest: function(xhr) {
						xhr.onreadystatechange = null;
						xhr.abort();
					}
				};
				var http_http = {
					createStreamingSocket(url) {
						return this.createSocket(http_streaming_socket, url);
					},
					createPollingSocket(url) {
						return this.createSocket(http_polling_socket, url);
					},
					createSocket(hooks, url) {
						return new http_socket(hooks, url);
					},
					createXHR(method, url) {
						return this.createRequest(http_xhr_request, method, url);
					},
					createRequest(hooks, method, url) {
						return new http_request_HTTPRequest(hooks, method, url);
					}
				};
				http_http.createXDR = function(method, url) {
					return this.createRequest(http_xdomain_request, method, url);
				};
				var runtime = {
					nextAuthCallbackID: 1,
					auth_callbacks: {},
					ScriptReceivers,
					DependenciesReceivers,
					getDefaultStrategy: default_strategy,
					Transports: transports_transports,
					transportConnectionInitializer: transport_connection_initializer,
					HTTPFactory: http_http,
					TimelineTransport: jsonp_timeline,
					getXHRAPI() {
						return window.XMLHttpRequest;
					},
					getWebSocketAPI() {
						return window.WebSocket || window.MozWebSocket;
					},
					setup(PusherClass) {
						window.Pusher = PusherClass;
						var initializeOnDocumentBody = () => {
							this.onDocumentBody(PusherClass.ready);
						};
						if (!window.JSON) Dependencies.load("json2", {}, initializeOnDocumentBody);
						else initializeOnDocumentBody();
					},
					getDocument() {
						return document;
					},
					getProtocol() {
						return this.getDocument().location.protocol;
					},
					getAuthorizers() {
						return {
							ajax: xhr_auth,
							jsonp: jsonp_auth
						};
					},
					onDocumentBody(callback) {
						if (document.body) callback();
						else setTimeout(() => {
							this.onDocumentBody(callback);
						}, 0);
					},
					createJSONPRequest(url, data) {
						return new jsonp_request_JSONPRequest(url, data);
					},
					createScriptRequest(src) {
						return new ScriptRequest(src);
					},
					getLocalStorage() {
						try {
							return window.localStorage;
						} catch (e) {
							return;
						}
					},
					createXHR() {
						if (this.getXHRAPI()) return this.createXMLHttpRequest();
						else return this.createMicrosoftXHR();
					},
					createXMLHttpRequest() {
						return new (this.getXHRAPI())();
					},
					createMicrosoftXHR() {
						return new ActiveXObject("Microsoft.XMLHTTP");
					},
					getNetwork() {
						return net_info_Network;
					},
					createWebSocket(url) {
						return new (this.getWebSocketAPI())(url);
					},
					createSocketRequest(method, url) {
						if (this.isXHRSupported()) return this.HTTPFactory.createXHR(method, url);
						else if (this.isXDRSupported(url.indexOf("https:") === 0)) return this.HTTPFactory.createXDR(method, url);
						else throw "Cross-origin HTTP requests are not supported";
					},
					isXHRSupported() {
						var Constructor = this.getXHRAPI();
						return Boolean(Constructor) && new Constructor().withCredentials !== void 0;
					},
					isXDRSupported(useTLS) {
						var protocol = useTLS ? "https:" : "http:";
						var documentProtocol = this.getProtocol();
						return Boolean(window["XDomainRequest"]) && documentProtocol === protocol;
					},
					addUnloadListener(listener) {
						if (window.addEventListener !== void 0) window.addEventListener("unload", listener, false);
						else if (window.attachEvent !== void 0) window.attachEvent("onunload", listener);
					},
					removeUnloadListener(listener) {
						if (window.addEventListener !== void 0) window.removeEventListener("unload", listener, false);
						else if (window.detachEvent !== void 0) window.detachEvent("onunload", listener);
					},
					randomInt(max) {
						const random = function() {
							return (window.crypto || window["msCrypto"]).getRandomValues(new Uint32Array(1))[0] / Math.pow(2, 32);
						};
						return Math.floor(random() * max);
					}
				};
				var TimelineLevel;
				(function(TimelineLevel$1) {
					TimelineLevel$1[TimelineLevel$1["ERROR"] = 3] = "ERROR";
					TimelineLevel$1[TimelineLevel$1["INFO"] = 6] = "INFO";
					TimelineLevel$1[TimelineLevel$1["DEBUG"] = 7] = "DEBUG";
				})(TimelineLevel || (TimelineLevel = {}));
				var timeline_level = TimelineLevel;
				class timeline_Timeline {
					constructor(key, session, options) {
						this.key = key;
						this.session = session;
						this.events = [];
						this.options = options || {};
						this.sent = 0;
						this.uniqueID = 0;
					}
					log(level, event) {
						if (level <= this.options.level) {
							this.events.push(extend$1({}, event, { timestamp: util.now() }));
							if (this.options.limit && this.events.length > this.options.limit) this.events.shift();
						}
					}
					error(event) {
						this.log(timeline_level.ERROR, event);
					}
					info(event) {
						this.log(timeline_level.INFO, event);
					}
					debug(event) {
						this.log(timeline_level.DEBUG, event);
					}
					isEmpty() {
						return this.events.length === 0;
					}
					send(sendfn, callback) {
						var data = extend$1({
							session: this.session,
							bundle: this.sent + 1,
							key: this.key,
							lib: "js",
							version: this.options.version,
							cluster: this.options.cluster,
							features: this.options.features,
							timeline: this.events
						}, this.options.params);
						this.events = [];
						sendfn(data, (error, result) => {
							if (!error) this.sent++;
							if (callback) callback(error, result);
						});
						return true;
					}
					generateUniqueID() {
						this.uniqueID++;
						return this.uniqueID;
					}
				}
				class transport_strategy_TransportStrategy {
					constructor(name, priority, transport, options) {
						this.name = name;
						this.priority = priority;
						this.transport = transport;
						this.options = options || {};
					}
					isSupported() {
						return this.transport.isSupported({ useTLS: this.options.useTLS });
					}
					connect(minPriority, callback) {
						if (!this.isSupported()) return failAttempt(new UnsupportedStrategy(), callback);
						else if (this.priority < minPriority) return failAttempt(new TransportPriorityTooLow(), callback);
						var connected = false;
						var transport = this.transport.createConnection(this.name, this.priority, this.options.key, this.options);
						var handshake = null;
						var onInitialized = function() {
							transport.unbind("initialized", onInitialized);
							transport.connect();
						};
						var onOpen = function() {
							handshake = factory$1.createHandshake(transport, function(result) {
								connected = true;
								unbindListeners();
								callback(null, result);
							});
						};
						var onError = function(error) {
							unbindListeners();
							callback(error);
						};
						var onClosed = function() {
							unbindListeners();
							callback(new TransportClosed(safeJSONStringify(transport)));
						};
						var unbindListeners = function() {
							transport.unbind("initialized", onInitialized);
							transport.unbind("open", onOpen);
							transport.unbind("error", onError);
							transport.unbind("closed", onClosed);
						};
						transport.bind("initialized", onInitialized);
						transport.bind("open", onOpen);
						transport.bind("error", onError);
						transport.bind("closed", onClosed);
						transport.initialize();
						return {
							abort: () => {
								if (connected) return;
								unbindListeners();
								if (handshake) handshake.close();
								else transport.close();
							},
							forceMinPriority: (p) => {
								if (connected) return;
								if (this.priority < p) if (handshake) handshake.close();
								else transport.close();
							}
						};
					}
				}
				function failAttempt(error, callback) {
					util.defer(function() {
						callback(error);
					});
					return {
						abort: function() {},
						forceMinPriority: function() {}
					};
				}
				const { Transports: strategy_builder_Transports } = runtime;
				var strategy_builder_defineTransport = function(config, name, type, priority, options, manager) {
					var transportClass = strategy_builder_Transports[type];
					if (!transportClass) throw new UnsupportedTransport(type);
					var enabled = (!config.enabledTransports || arrayIndexOf(config.enabledTransports, name) !== -1) && (!config.disabledTransports || arrayIndexOf(config.disabledTransports, name) === -1);
					var transport;
					if (enabled) {
						options = Object.assign({ ignoreNullOrigin: config.ignoreNullOrigin }, options);
						transport = new transport_strategy_TransportStrategy(name, priority, manager ? manager.getAssistant(transportClass) : transportClass, options);
					} else transport = strategy_builder_UnsupportedStrategy;
					return transport;
				};
				var strategy_builder_UnsupportedStrategy = {
					isSupported: function() {
						return false;
					},
					connect: function(_, callback) {
						var deferred = util.defer(function() {
							callback(new UnsupportedStrategy());
						});
						return {
							abort: function() {
								deferred.ensureAborted();
							},
							forceMinPriority: function() {}
						};
					}
				};
				function validateOptions(options) {
					if (options == null) throw "You must pass an options object";
					if (options.cluster == null) throw "Options object must provide a cluster";
					if ("disableStats" in options) logger.warn("The disableStats option is deprecated in favor of enableStats");
				}
				const composeChannelQuery = (params, authOptions) => {
					var query = "socket_id=" + encodeURIComponent(params.socketId);
					for (var key in authOptions.params) query += "&" + encodeURIComponent(key) + "=" + encodeURIComponent(authOptions.params[key]);
					if (authOptions.paramsProvider != null) {
						let dynamicParams = authOptions.paramsProvider();
						for (var key in dynamicParams) query += "&" + encodeURIComponent(key) + "=" + encodeURIComponent(dynamicParams[key]);
					}
					return query;
				};
				const UserAuthenticator = (authOptions) => {
					if (typeof runtime.getAuthorizers()[authOptions.transport] === "undefined") throw `'${authOptions.transport}' is not a recognized auth transport`;
					return (params, callback) => {
						const query = composeChannelQuery(params, authOptions);
						runtime.getAuthorizers()[authOptions.transport](runtime, query, authOptions, AuthRequestType.UserAuthentication, callback);
					};
				};
				var user_authenticator = UserAuthenticator;
				const channel_authorizer_composeChannelQuery = (params, authOptions) => {
					var query = "socket_id=" + encodeURIComponent(params.socketId);
					query += "&channel_name=" + encodeURIComponent(params.channelName);
					for (var key in authOptions.params) query += "&" + encodeURIComponent(key) + "=" + encodeURIComponent(authOptions.params[key]);
					if (authOptions.paramsProvider != null) {
						let dynamicParams = authOptions.paramsProvider();
						for (var key in dynamicParams) query += "&" + encodeURIComponent(key) + "=" + encodeURIComponent(dynamicParams[key]);
					}
					return query;
				};
				const ChannelAuthorizer = (authOptions) => {
					if (typeof runtime.getAuthorizers()[authOptions.transport] === "undefined") throw `'${authOptions.transport}' is not a recognized auth transport`;
					return (params, callback) => {
						const query = channel_authorizer_composeChannelQuery(params, authOptions);
						runtime.getAuthorizers()[authOptions.transport](runtime, query, authOptions, AuthRequestType.ChannelAuthorization, callback);
					};
				};
				var channel_authorizer = ChannelAuthorizer;
				const ChannelAuthorizerProxy = (pusher, authOptions, channelAuthorizerGenerator) => {
					const deprecatedAuthorizerOptions = {
						authTransport: authOptions.transport,
						authEndpoint: authOptions.endpoint,
						auth: {
							params: authOptions.params,
							headers: authOptions.headers
						}
					};
					return (params, callback) => {
						channelAuthorizerGenerator(pusher.channel(params.channelName), deprecatedAuthorizerOptions).authorize(params.socketId, callback);
					};
				};
				function getConfig(opts, pusher) {
					let config = {
						activityTimeout: opts.activityTimeout || defaults$1.activityTimeout,
						cluster: opts.cluster,
						httpPath: opts.httpPath || defaults$1.httpPath,
						httpPort: opts.httpPort || defaults$1.httpPort,
						httpsPort: opts.httpsPort || defaults$1.httpsPort,
						pongTimeout: opts.pongTimeout || defaults$1.pongTimeout,
						statsHost: opts.statsHost || defaults$1.stats_host,
						unavailableTimeout: opts.unavailableTimeout || defaults$1.unavailableTimeout,
						wsPath: opts.wsPath || defaults$1.wsPath,
						wsPort: opts.wsPort || defaults$1.wsPort,
						wssPort: opts.wssPort || defaults$1.wssPort,
						enableStats: getEnableStatsConfig(opts),
						httpHost: getHttpHost(opts),
						useTLS: shouldUseTLS(opts),
						wsHost: getWebsocketHost(opts),
						userAuthenticator: buildUserAuthenticator(opts),
						channelAuthorizer: buildChannelAuthorizer(opts, pusher)
					};
					if ("disabledTransports" in opts) config.disabledTransports = opts.disabledTransports;
					if ("enabledTransports" in opts) config.enabledTransports = opts.enabledTransports;
					if ("ignoreNullOrigin" in opts) config.ignoreNullOrigin = opts.ignoreNullOrigin;
					if ("timelineParams" in opts) config.timelineParams = opts.timelineParams;
					if ("nacl" in opts) config.nacl = opts.nacl;
					return config;
				}
				function getHttpHost(opts) {
					if (opts.httpHost) return opts.httpHost;
					if (opts.cluster) return `sockjs-${opts.cluster}.pusher.com`;
					return defaults$1.httpHost;
				}
				function getWebsocketHost(opts) {
					if (opts.wsHost) return opts.wsHost;
					return getWebsocketHostFromCluster(opts.cluster);
				}
				function getWebsocketHostFromCluster(cluster) {
					return `ws-${cluster}.pusher.com`;
				}
				function shouldUseTLS(opts) {
					if (runtime.getProtocol() === "https:") return true;
					else if (opts.forceTLS === false) return false;
					return true;
				}
				function getEnableStatsConfig(opts) {
					if ("enableStats" in opts) return opts.enableStats;
					if ("disableStats" in opts) return !opts.disableStats;
					return false;
				}
				function buildUserAuthenticator(opts) {
					const userAuthentication = Object.assign(Object.assign({}, defaults$1.userAuthentication), opts.userAuthentication);
					if ("customHandler" in userAuthentication && userAuthentication["customHandler"] != null) return userAuthentication["customHandler"];
					return user_authenticator(userAuthentication);
				}
				function buildChannelAuth(opts, pusher) {
					let channelAuthorization;
					if ("channelAuthorization" in opts) channelAuthorization = Object.assign(Object.assign({}, defaults$1.channelAuthorization), opts.channelAuthorization);
					else {
						channelAuthorization = {
							transport: opts.authTransport || defaults$1.authTransport,
							endpoint: opts.authEndpoint || defaults$1.authEndpoint
						};
						if ("auth" in opts) {
							if ("params" in opts.auth) channelAuthorization.params = opts.auth.params;
							if ("headers" in opts.auth) channelAuthorization.headers = opts.auth.headers;
						}
						if ("authorizer" in opts) channelAuthorization.customHandler = ChannelAuthorizerProxy(pusher, channelAuthorization, opts.authorizer);
					}
					return channelAuthorization;
				}
				function buildChannelAuthorizer(opts, pusher) {
					const channelAuthorization = buildChannelAuth(opts, pusher);
					if ("customHandler" in channelAuthorization && channelAuthorization["customHandler"] != null) return channelAuthorization["customHandler"];
					return channel_authorizer(channelAuthorization);
				}
				class watchlist_WatchlistFacade extends dispatcher_Dispatcher {
					constructor(pusher) {
						super(function(eventName, data) {
							logger.debug(`No callbacks on watchlist events for ${eventName}`);
						});
						this.pusher = pusher;
						this.bindWatchlistInternalEvent();
					}
					handleEvent(pusherEvent) {
						pusherEvent.data.events.forEach((watchlistEvent) => {
							this.emit(watchlistEvent.name, watchlistEvent);
						});
					}
					bindWatchlistInternalEvent() {
						this.pusher.connection.bind("message", (pusherEvent) => {
							if (pusherEvent.event === "pusher_internal:watchlist_events") this.handleEvent(pusherEvent);
						});
					}
				}
				function flatPromise() {
					let resolve, reject;
					return {
						promise: new Promise((res, rej) => {
							resolve = res;
							reject = rej;
						}),
						resolve,
						reject
					};
				}
				var flat_promise = flatPromise;
				class user_UserFacade extends dispatcher_Dispatcher {
					constructor(pusher) {
						super(function(eventName, data) {
							logger.debug("No callbacks on user for " + eventName);
						});
						this.signin_requested = false;
						this.user_data = null;
						this.serverToUserChannel = null;
						this.signinDonePromise = null;
						this._signinDoneResolve = null;
						this._onAuthorize = (err, authData) => {
							if (err) {
								logger.warn(`Error during signin: ${err}`);
								this._cleanup();
								return;
							}
							this.pusher.send_event("pusher:signin", {
								auth: authData.auth,
								user_data: authData.user_data
							});
						};
						this.pusher = pusher;
						this.pusher.connection.bind("state_change", ({ previous, current }) => {
							if (previous !== "connected" && current === "connected") this._signin();
							if (previous === "connected" && current !== "connected") {
								this._cleanup();
								this._newSigninPromiseIfNeeded();
							}
						});
						this.watchlist = new watchlist_WatchlistFacade(pusher);
						this.pusher.connection.bind("message", (event) => {
							if (event.event === "pusher:signin_success") this._onSigninSuccess(event.data);
							if (this.serverToUserChannel && this.serverToUserChannel.name === event.channel) this.serverToUserChannel.handleEvent(event);
						});
					}
					signin() {
						if (this.signin_requested) return;
						this.signin_requested = true;
						this._signin();
					}
					_signin() {
						if (!this.signin_requested) return;
						this._newSigninPromiseIfNeeded();
						if (this.pusher.connection.state !== "connected") return;
						this.pusher.config.userAuthenticator({ socketId: this.pusher.connection.socket_id }, this._onAuthorize);
					}
					_onSigninSuccess(data) {
						try {
							this.user_data = JSON.parse(data.user_data);
						} catch (e) {
							logger.error(`Failed parsing user data after signin: ${data.user_data}`);
							this._cleanup();
							return;
						}
						if (typeof this.user_data.id !== "string" || this.user_data.id === "") {
							logger.error(`user_data doesn't contain an id. user_data: ${this.user_data}`);
							this._cleanup();
							return;
						}
						this._signinDoneResolve();
						this._subscribeChannels();
					}
					_subscribeChannels() {
						const ensure_subscribed = (channel) => {
							if (channel.subscriptionPending && channel.subscriptionCancelled) channel.reinstateSubscription();
							else if (!channel.subscriptionPending && this.pusher.connection.state === "connected") channel.subscribe();
						};
						this.serverToUserChannel = new channel_Channel(`#server-to-user-${this.user_data.id}`, this.pusher);
						this.serverToUserChannel.bind_global((eventName, data) => {
							if (eventName.indexOf("pusher_internal:") === 0 || eventName.indexOf("pusher:") === 0) return;
							this.emit(eventName, data);
						});
						ensure_subscribed(this.serverToUserChannel);
					}
					_cleanup() {
						this.user_data = null;
						if (this.serverToUserChannel) {
							this.serverToUserChannel.unbind_all();
							this.serverToUserChannel.disconnect();
							this.serverToUserChannel = null;
						}
						if (this.signin_requested) this._signinDoneResolve();
					}
					_newSigninPromiseIfNeeded() {
						if (!this.signin_requested) return;
						if (this.signinDonePromise && !this.signinDonePromise.done) return;
						const { promise, resolve, reject: _ } = flat_promise();
						promise.done = false;
						const setDone = () => {
							promise.done = true;
						};
						promise.then(setDone).catch(setDone);
						this.signinDonePromise = promise;
						this._signinDoneResolve = resolve;
					}
				}
				class pusher_Pusher {
					static ready() {
						pusher_Pusher.isReady = true;
						for (var i = 0, l$1 = pusher_Pusher.instances.length; i < l$1; i++) pusher_Pusher.instances[i].connect();
					}
					static getClientFeatures() {
						return keys(filterObject({ ws: runtime.Transports.ws }, function(t) {
							return t.isSupported({});
						}));
					}
					constructor(app_key, options) {
						checkAppKey(app_key);
						validateOptions(options);
						this.key = app_key;
						this.config = getConfig(options, this);
						this.channels = factory$1.createChannels();
						this.global_emitter = new dispatcher_Dispatcher();
						this.sessionID = runtime.randomInt(1e9);
						this.timeline = new timeline_Timeline(this.key, this.sessionID, {
							cluster: this.config.cluster,
							features: pusher_Pusher.getClientFeatures(),
							params: this.config.timelineParams || {},
							limit: 50,
							level: timeline_level.INFO,
							version: defaults$1.VERSION
						});
						if (this.config.enableStats) this.timelineSender = factory$1.createTimelineSender(this.timeline, {
							host: this.config.statsHost,
							path: "/timeline/v2/" + runtime.TimelineTransport.name
						});
						var getStrategy = (options$1) => {
							return runtime.getDefaultStrategy(this.config, options$1, strategy_builder_defineTransport);
						};
						this.connection = factory$1.createConnectionManager(this.key, {
							getStrategy,
							timeline: this.timeline,
							activityTimeout: this.config.activityTimeout,
							pongTimeout: this.config.pongTimeout,
							unavailableTimeout: this.config.unavailableTimeout,
							useTLS: Boolean(this.config.useTLS)
						});
						this.connection.bind("connected", () => {
							this.subscribeAll();
							if (this.timelineSender) this.timelineSender.send(this.connection.isUsingTLS());
						});
						this.connection.bind("message", (event) => {
							var internal = event.event.indexOf("pusher_internal:") === 0;
							if (event.channel) {
								var channel = this.channel(event.channel);
								if (channel) channel.handleEvent(event);
							}
							if (!internal) this.global_emitter.emit(event.event, event.data);
						});
						this.connection.bind("connecting", () => {
							this.channels.disconnect();
						});
						this.connection.bind("disconnected", () => {
							this.channels.disconnect();
						});
						this.connection.bind("error", (err) => {
							logger.warn(err);
						});
						pusher_Pusher.instances.push(this);
						this.timeline.info({ instances: pusher_Pusher.instances.length });
						this.user = new user_UserFacade(this);
						if (pusher_Pusher.isReady) this.connect();
					}
					channel(name) {
						return this.channels.find(name);
					}
					allChannels() {
						return this.channels.all();
					}
					connect() {
						this.connection.connect();
						if (this.timelineSender) {
							if (!this.timelineSenderTimer) {
								var usingTLS = this.connection.isUsingTLS();
								var timelineSender = this.timelineSender;
								this.timelineSenderTimer = new timers_PeriodicTimer(6e4, function() {
									timelineSender.send(usingTLS);
								});
							}
						}
					}
					disconnect() {
						this.connection.disconnect();
						if (this.timelineSenderTimer) {
							this.timelineSenderTimer.ensureAborted();
							this.timelineSenderTimer = null;
						}
					}
					bind(event_name, callback, context) {
						this.global_emitter.bind(event_name, callback, context);
						return this;
					}
					unbind(event_name, callback, context) {
						this.global_emitter.unbind(event_name, callback, context);
						return this;
					}
					bind_global(callback) {
						this.global_emitter.bind_global(callback);
						return this;
					}
					unbind_global(callback) {
						this.global_emitter.unbind_global(callback);
						return this;
					}
					unbind_all(callback) {
						this.global_emitter.unbind_all();
						return this;
					}
					subscribeAll() {
						var channelName;
						for (channelName in this.channels.channels) if (this.channels.channels.hasOwnProperty(channelName)) this.subscribe(channelName);
					}
					subscribe(channel_name) {
						var channel = this.channels.add(channel_name, this);
						if (channel.subscriptionPending && channel.subscriptionCancelled) channel.reinstateSubscription();
						else if (!channel.subscriptionPending && this.connection.state === "connected") channel.subscribe();
						return channel;
					}
					unsubscribe(channel_name) {
						var channel = this.channels.find(channel_name);
						if (channel && channel.subscriptionPending) channel.cancelSubscription();
						else {
							channel = this.channels.remove(channel_name);
							if (channel && channel.subscribed) channel.unsubscribe();
						}
					}
					send_event(event_name, data, channel) {
						return this.connection.send_event(event_name, data, channel);
					}
					shouldUseTLS() {
						return this.config.useTLS;
					}
					signin() {
						this.user.signin();
					}
				}
				pusher_Pusher.instances = [];
				pusher_Pusher.isReady = false;
				pusher_Pusher.logToConsole = false;
				pusher_Pusher.Runtime = runtime;
				pusher_Pusher.ScriptReceivers = runtime.ScriptReceivers;
				pusher_Pusher.DependenciesReceivers = runtime.DependenciesReceivers;
				pusher_Pusher.auth_callbacks = runtime.auth_callbacks;
				var core_pusher = __webpack_exports__["default"] = pusher_Pusher;
				function checkAppKey(key) {
					if (key === null || key === void 0) throw "You must pass your app key when you instantiate Pusher.";
				}
				runtime.setup(pusher_Pusher);
			})
		]);
	});
}));
function bind(fn, thisArg) {
	return function wrap() {
		return fn.apply(thisArg, arguments);
	};
}
var { toString } = Object.prototype;
var { getPrototypeOf } = Object;
var { iterator, toStringTag } = Symbol;
var kindOf = ((cache) => (thing) => {
	const str = toString.call(thing);
	return cache[str] || (cache[str] = str.slice(8, -1).toLowerCase());
})(Object.create(null));
var kindOfTest = (type) => {
	type = type.toLowerCase();
	return (thing) => kindOf(thing) === type;
};
var typeOfTest = (type) => (thing) => typeof thing === type;
var { isArray } = Array;
var isUndefined = typeOfTest("undefined");
function isBuffer(val) {
	return val !== null && !isUndefined(val) && val.constructor !== null && !isUndefined(val.constructor) && isFunction$1(val.constructor.isBuffer) && val.constructor.isBuffer(val);
}
var isArrayBuffer = kindOfTest("ArrayBuffer");
function isArrayBufferView(val) {
	let result;
	if (typeof ArrayBuffer !== "undefined" && ArrayBuffer.isView) result = ArrayBuffer.isView(val);
	else result = val && val.buffer && isArrayBuffer(val.buffer);
	return result;
}
var isString = typeOfTest("string");
var isFunction$1 = typeOfTest("function");
var isNumber = typeOfTest("number");
var isObject = (thing) => thing !== null && typeof thing === "object";
var isBoolean = (thing) => thing === true || thing === false;
var isPlainObject = (val) => {
	if (kindOf(val) !== "object") return false;
	const prototype$2 = getPrototypeOf(val);
	return (prototype$2 === null || prototype$2 === Object.prototype || Object.getPrototypeOf(prototype$2) === null) && !(toStringTag in val) && !(iterator in val);
};
var isEmptyObject = (val) => {
	if (!isObject(val) || isBuffer(val)) return false;
	try {
		return Object.keys(val).length === 0 && Object.getPrototypeOf(val) === Object.prototype;
	} catch (e) {
		return false;
	}
};
var isDate = kindOfTest("Date");
var isFile = kindOfTest("File");
var isBlob = kindOfTest("Blob");
var isFileList = kindOfTest("FileList");
var isStream = (val) => isObject(val) && isFunction$1(val.pipe);
var isFormData = (thing) => {
	let kind;
	return thing && (typeof FormData === "function" && thing instanceof FormData || isFunction$1(thing.append) && ((kind = kindOf(thing)) === "formdata" || kind === "object" && isFunction$1(thing.toString) && thing.toString() === "[object FormData]"));
};
var isURLSearchParams = kindOfTest("URLSearchParams");
var [isReadableStream, isRequest, isResponse, isHeaders] = [
	"ReadableStream",
	"Request",
	"Response",
	"Headers"
].map(kindOfTest);
var trim = (str) => str.trim ? str.trim() : str.replace(/^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g, "");
function forEach(obj, fn, { allOwnKeys = false } = {}) {
	if (obj === null || typeof obj === "undefined") return;
	let i;
	let l;
	if (typeof obj !== "object") obj = [obj];
	if (isArray(obj)) for (i = 0, l = obj.length; i < l; i++) fn.call(null, obj[i], i, obj);
	else {
		if (isBuffer(obj)) return;
		const keys = allOwnKeys ? Object.getOwnPropertyNames(obj) : Object.keys(obj);
		const len = keys.length;
		let key;
		for (i = 0; i < len; i++) {
			key = keys[i];
			fn.call(null, obj[key], key, obj);
		}
	}
}
function findKey(obj, key) {
	if (isBuffer(obj)) return null;
	key = key.toLowerCase();
	const keys = Object.keys(obj);
	let i = keys.length;
	let _key;
	while (i-- > 0) {
		_key = keys[i];
		if (key === _key.toLowerCase()) return _key;
	}
	return null;
}
var _global = (() => {
	if (typeof globalThis !== "undefined") return globalThis;
	return typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : global;
})();
var isContextDefined = (context) => !isUndefined(context) && context !== _global;
function merge() {
	const { caseless, skipUndefined } = isContextDefined(this) && this || {};
	const result = {};
	const assignValue = (val, key) => {
		const targetKey = caseless && findKey(result, key) || key;
		if (isPlainObject(result[targetKey]) && isPlainObject(val)) result[targetKey] = merge(result[targetKey], val);
		else if (isPlainObject(val)) result[targetKey] = merge({}, val);
		else if (isArray(val)) result[targetKey] = val.slice();
		else if (!skipUndefined || !isUndefined(val)) result[targetKey] = val;
	};
	for (let i = 0, l = arguments.length; i < l; i++) arguments[i] && forEach(arguments[i], assignValue);
	return result;
}
var extend = (a, b, thisArg, { allOwnKeys } = {}) => {
	forEach(b, (val, key) => {
		if (thisArg && isFunction$1(val)) a[key] = bind(val, thisArg);
		else a[key] = val;
	}, { allOwnKeys });
	return a;
};
var stripBOM = (content) => {
	if (content.charCodeAt(0) === 65279) content = content.slice(1);
	return content;
};
var inherits = (constructor, superConstructor, props, descriptors$1) => {
	constructor.prototype = Object.create(superConstructor.prototype, descriptors$1);
	constructor.prototype.constructor = constructor;
	Object.defineProperty(constructor, "super", { value: superConstructor.prototype });
	props && Object.assign(constructor.prototype, props);
};
var toFlatObject = (sourceObj, destObj, filter, propFilter) => {
	let props;
	let i;
	let prop;
	const merged = {};
	destObj = destObj || {};
	if (sourceObj == null) return destObj;
	do {
		props = Object.getOwnPropertyNames(sourceObj);
		i = props.length;
		while (i-- > 0) {
			prop = props[i];
			if ((!propFilter || propFilter(prop, sourceObj, destObj)) && !merged[prop]) {
				destObj[prop] = sourceObj[prop];
				merged[prop] = true;
			}
		}
		sourceObj = filter !== false && getPrototypeOf(sourceObj);
	} while (sourceObj && (!filter || filter(sourceObj, destObj)) && sourceObj !== Object.prototype);
	return destObj;
};
var endsWith = (str, searchString, position) => {
	str = String(str);
	if (position === void 0 || position > str.length) position = str.length;
	position -= searchString.length;
	const lastIndex = str.indexOf(searchString, position);
	return lastIndex !== -1 && lastIndex === position;
};
var toArray = (thing) => {
	if (!thing) return null;
	if (isArray(thing)) return thing;
	let i = thing.length;
	if (!isNumber(i)) return null;
	const arr = new Array(i);
	while (i-- > 0) arr[i] = thing[i];
	return arr;
};
var isTypedArray = ((TypedArray) => {
	return (thing) => {
		return TypedArray && thing instanceof TypedArray;
	};
})(typeof Uint8Array !== "undefined" && getPrototypeOf(Uint8Array));
var forEachEntry = (obj, fn) => {
	const _iterator = (obj && obj[iterator]).call(obj);
	let result;
	while ((result = _iterator.next()) && !result.done) {
		const pair = result.value;
		fn.call(obj, pair[0], pair[1]);
	}
};
var matchAll = (regExp, str) => {
	let matches;
	const arr = [];
	while ((matches = regExp.exec(str)) !== null) arr.push(matches);
	return arr;
};
var isHTMLForm = kindOfTest("HTMLFormElement");
var toCamelCase = (str) => {
	return str.toLowerCase().replace(/[-_\s]([a-z\d])(\w*)/g, function replacer(m, p1, p2) {
		return p1.toUpperCase() + p2;
	});
};
var hasOwnProperty = (({ hasOwnProperty: hasOwnProperty$1 }) => (obj, prop) => hasOwnProperty$1.call(obj, prop))(Object.prototype);
var isRegExp = kindOfTest("RegExp");
var reduceDescriptors = (obj, reducer) => {
	const descriptors$1 = Object.getOwnPropertyDescriptors(obj);
	const reducedDescriptors = {};
	forEach(descriptors$1, (descriptor, name) => {
		let ret;
		if ((ret = reducer(descriptor, name, obj)) !== false) reducedDescriptors[name] = ret || descriptor;
	});
	Object.defineProperties(obj, reducedDescriptors);
};
var freezeMethods = (obj) => {
	reduceDescriptors(obj, (descriptor, name) => {
		if (isFunction$1(obj) && [
			"arguments",
			"caller",
			"callee"
		].indexOf(name) !== -1) return false;
		const value = obj[name];
		if (!isFunction$1(value)) return;
		descriptor.enumerable = false;
		if ("writable" in descriptor) {
			descriptor.writable = false;
			return;
		}
		if (!descriptor.set) descriptor.set = () => {
			throw Error("Can not rewrite read-only method '" + name + "'");
		};
	});
};
var toObjectSet = (arrayOrString, delimiter) => {
	const obj = {};
	const define$1 = (arr) => {
		arr.forEach((value) => {
			obj[value] = true;
		});
	};
	isArray(arrayOrString) ? define$1(arrayOrString) : define$1(String(arrayOrString).split(delimiter));
	return obj;
};
var noop = () => {};
var toFiniteNumber = (value, defaultValue) => {
	return value != null && Number.isFinite(value = +value) ? value : defaultValue;
};
function isSpecCompliantForm(thing) {
	return !!(thing && isFunction$1(thing.append) && thing[toStringTag] === "FormData" && thing[iterator]);
}
var toJSONObject = (obj) => {
	const stack = new Array(10);
	const visit = (source, i) => {
		if (isObject(source)) {
			if (stack.indexOf(source) >= 0) return;
			if (isBuffer(source)) return source;
			if (!("toJSON" in source)) {
				stack[i] = source;
				const target = isArray(source) ? [] : {};
				forEach(source, (value, key) => {
					const reducedValue = visit(value, i + 1);
					!isUndefined(reducedValue) && (target[key] = reducedValue);
				});
				stack[i] = void 0;
				return target;
			}
		}
		return source;
	};
	return visit(obj, 0);
};
var isAsyncFn = kindOfTest("AsyncFunction");
var isThenable = (thing) => thing && (isObject(thing) || isFunction$1(thing)) && isFunction$1(thing.then) && isFunction$1(thing.catch);
var _setImmediate = ((setImmediateSupported, postMessageSupported) => {
	if (setImmediateSupported) return setImmediate;
	return postMessageSupported ? ((token, callbacks) => {
		_global.addEventListener("message", ({ source, data }) => {
			if (source === _global && data === token) callbacks.length && callbacks.shift()();
		}, false);
		return (cb) => {
			callbacks.push(cb);
			_global.postMessage(token, "*");
		};
	})(`axios@${Math.random()}`, []) : (cb) => setTimeout(cb);
})(typeof setImmediate === "function", isFunction$1(_global.postMessage));
var asap = typeof queueMicrotask !== "undefined" ? queueMicrotask.bind(_global) : typeof process !== "undefined" && process.nextTick || _setImmediate;
var isIterable = (thing) => thing != null && isFunction$1(thing[iterator]);
var utils_default = {
	isArray,
	isArrayBuffer,
	isBuffer,
	isFormData,
	isArrayBufferView,
	isString,
	isNumber,
	isBoolean,
	isObject,
	isPlainObject,
	isEmptyObject,
	isReadableStream,
	isRequest,
	isResponse,
	isHeaders,
	isUndefined,
	isDate,
	isFile,
	isBlob,
	isRegExp,
	isFunction: isFunction$1,
	isStream,
	isURLSearchParams,
	isTypedArray,
	isFileList,
	forEach,
	merge,
	extend,
	trim,
	stripBOM,
	inherits,
	toFlatObject,
	kindOf,
	kindOfTest,
	endsWith,
	toArray,
	forEachEntry,
	matchAll,
	isHTMLForm,
	hasOwnProperty,
	hasOwnProp: hasOwnProperty,
	reduceDescriptors,
	freezeMethods,
	toObjectSet,
	toCamelCase,
	noop,
	toFiniteNumber,
	findKey,
	global: _global,
	isContextDefined,
	isSpecCompliantForm,
	toJSONObject,
	isAsyncFn,
	isThenable,
	setImmediate: _setImmediate,
	asap,
	isIterable
};
function AxiosError(message, code, config, request, response) {
	Error.call(this);
	if (Error.captureStackTrace) Error.captureStackTrace(this, this.constructor);
	else this.stack = (/* @__PURE__ */ new Error()).stack;
	this.message = message;
	this.name = "AxiosError";
	code && (this.code = code);
	config && (this.config = config);
	request && (this.request = request);
	if (response) {
		this.response = response;
		this.status = response.status ? response.status : null;
	}
}
utils_default.inherits(AxiosError, Error, { toJSON: function toJSON() {
	return {
		message: this.message,
		name: this.name,
		description: this.description,
		number: this.number,
		fileName: this.fileName,
		lineNumber: this.lineNumber,
		columnNumber: this.columnNumber,
		stack: this.stack,
		config: utils_default.toJSONObject(this.config),
		code: this.code,
		status: this.status
	};
} });
var prototype$1 = AxiosError.prototype;
var descriptors = {};
[
	"ERR_BAD_OPTION_VALUE",
	"ERR_BAD_OPTION",
	"ECONNABORTED",
	"ETIMEDOUT",
	"ERR_NETWORK",
	"ERR_FR_TOO_MANY_REDIRECTS",
	"ERR_DEPRECATED",
	"ERR_BAD_RESPONSE",
	"ERR_BAD_REQUEST",
	"ERR_CANCELED",
	"ERR_NOT_SUPPORT",
	"ERR_INVALID_URL"
].forEach((code) => {
	descriptors[code] = { value: code };
});
Object.defineProperties(AxiosError, descriptors);
Object.defineProperty(prototype$1, "isAxiosError", { value: true });
AxiosError.from = (error, code, config, request, response, customProps) => {
	const axiosError = Object.create(prototype$1);
	utils_default.toFlatObject(error, axiosError, function filter(obj) {
		return obj !== Error.prototype;
	}, (prop) => {
		return prop !== "isAxiosError";
	});
	const msg = error && error.message ? error.message : "Error";
	const errCode = code == null && error ? error.code : code;
	AxiosError.call(axiosError, msg, errCode, config, request, response);
	if (error && axiosError.cause == null) Object.defineProperty(axiosError, "cause", {
		value: error,
		configurable: true
	});
	axiosError.name = error && error.name || "Error";
	customProps && Object.assign(axiosError, customProps);
	return axiosError;
};
var AxiosError_default = AxiosError;
function isVisitable(thing) {
	return utils_default.isPlainObject(thing) || utils_default.isArray(thing);
}
function removeBrackets(key) {
	return utils_default.endsWith(key, "[]") ? key.slice(0, -2) : key;
}
function renderKey(path, key, dots) {
	if (!path) return key;
	return path.concat(key).map(function each(token, i) {
		token = removeBrackets(token);
		return !dots && i ? "[" + token + "]" : token;
	}).join(dots ? "." : "");
}
function isFlatArray(arr) {
	return utils_default.isArray(arr) && !arr.some(isVisitable);
}
var predicates = utils_default.toFlatObject(utils_default, {}, null, function filter(prop) {
	return /^is[A-Z]/.test(prop);
});
function toFormData(obj, formData, options) {
	if (!utils_default.isObject(obj)) throw new TypeError("target must be an object");
	formData = formData || new FormData();
	options = utils_default.toFlatObject(options, {
		metaTokens: true,
		dots: false,
		indexes: false
	}, false, function defined(option, source) {
		return !utils_default.isUndefined(source[option]);
	});
	const metaTokens = options.metaTokens;
	const visitor = options.visitor || defaultVisitor;
	const dots = options.dots;
	const indexes = options.indexes;
	const useBlob = (options.Blob || typeof Blob !== "undefined" && Blob) && utils_default.isSpecCompliantForm(formData);
	if (!utils_default.isFunction(visitor)) throw new TypeError("visitor must be a function");
	function convertValue(value) {
		if (value === null) return "";
		if (utils_default.isDate(value)) return value.toISOString();
		if (utils_default.isBoolean(value)) return value.toString();
		if (!useBlob && utils_default.isBlob(value)) throw new AxiosError_default("Blob is not supported. Use a Buffer instead.");
		if (utils_default.isArrayBuffer(value) || utils_default.isTypedArray(value)) return useBlob && typeof Blob === "function" ? new Blob([value]) : Buffer.from(value);
		return value;
	}
	function defaultVisitor(value, key, path) {
		let arr = value;
		if (value && !path && typeof value === "object") {
			if (utils_default.endsWith(key, "{}")) {
				key = metaTokens ? key : key.slice(0, -2);
				value = JSON.stringify(value);
			} else if (utils_default.isArray(value) && isFlatArray(value) || (utils_default.isFileList(value) || utils_default.endsWith(key, "[]")) && (arr = utils_default.toArray(value))) {
				key = removeBrackets(key);
				arr.forEach(function each(el, index) {
					!(utils_default.isUndefined(el) || el === null) && formData.append(indexes === true ? renderKey([key], index, dots) : indexes === null ? key : key + "[]", convertValue(el));
				});
				return false;
			}
		}
		if (isVisitable(value)) return true;
		formData.append(renderKey(path, key, dots), convertValue(value));
		return false;
	}
	const stack = [];
	const exposedHelpers = Object.assign(predicates, {
		defaultVisitor,
		convertValue,
		isVisitable
	});
	function build(value, path) {
		if (utils_default.isUndefined(value)) return;
		if (stack.indexOf(value) !== -1) throw Error("Circular reference detected in " + path.join("."));
		stack.push(value);
		utils_default.forEach(value, function each(el, key) {
			if ((!(utils_default.isUndefined(el) || el === null) && visitor.call(formData, el, utils_default.isString(key) ? key.trim() : key, path, exposedHelpers)) === true) build(el, path ? path.concat(key) : [key]);
		});
		stack.pop();
	}
	if (!utils_default.isObject(obj)) throw new TypeError("data must be an object");
	build(obj);
	return formData;
}
var toFormData_default = toFormData;
function encode$1(str) {
	const charMap = {
		"!": "%21",
		"'": "%27",
		"(": "%28",
		")": "%29",
		"~": "%7E",
		"%20": "+",
		"%00": "\0"
	};
	return encodeURIComponent(str).replace(/[!'()~]|%20|%00/g, function replacer(match) {
		return charMap[match];
	});
}
function AxiosURLSearchParams(params, options) {
	this._pairs = [];
	params && toFormData_default(params, this, options);
}
var prototype = AxiosURLSearchParams.prototype;
prototype.append = function append(name, value) {
	this._pairs.push([name, value]);
};
prototype.toString = function toString$1(encoder) {
	const _encode = encoder ? function(value) {
		return encoder.call(this, value, encode$1);
	} : encode$1;
	return this._pairs.map(function each(pair) {
		return _encode(pair[0]) + "=" + _encode(pair[1]);
	}, "").join("&");
};
var AxiosURLSearchParams_default = AxiosURLSearchParams;
function encode(val) {
	return encodeURIComponent(val).replace(/%3A/gi, ":").replace(/%24/g, "$").replace(/%2C/gi, ",").replace(/%20/g, "+");
}
function buildURL(url, params, options) {
	if (!params) return url;
	const _encode = options && options.encode || encode;
	if (utils_default.isFunction(options)) options = { serialize: options };
	const serializeFn = options && options.serialize;
	let serializedParams;
	if (serializeFn) serializedParams = serializeFn(params, options);
	else serializedParams = utils_default.isURLSearchParams(params) ? params.toString() : new AxiosURLSearchParams_default(params, options).toString(_encode);
	if (serializedParams) {
		const hashmarkIndex = url.indexOf("#");
		if (hashmarkIndex !== -1) url = url.slice(0, hashmarkIndex);
		url += (url.indexOf("?") === -1 ? "?" : "&") + serializedParams;
	}
	return url;
}
var InterceptorManager = class {
	constructor() {
		this.handlers = [];
	}
	use(fulfilled, rejected, options) {
		this.handlers.push({
			fulfilled,
			rejected,
			synchronous: options ? options.synchronous : false,
			runWhen: options ? options.runWhen : null
		});
		return this.handlers.length - 1;
	}
	eject(id) {
		if (this.handlers[id]) this.handlers[id] = null;
	}
	clear() {
		if (this.handlers) this.handlers = [];
	}
	forEach(fn) {
		utils_default.forEach(this.handlers, function forEachHandler(h) {
			if (h !== null) fn(h);
		});
	}
};
var InterceptorManager_default = InterceptorManager;
var transitional_default = {
	silentJSONParsing: true,
	forcedJSONParsing: true,
	clarifyTimeoutError: false
};
var browser_default = {
	isBrowser: true,
	classes: {
		URLSearchParams: typeof URLSearchParams !== "undefined" ? URLSearchParams : AxiosURLSearchParams_default,
		FormData: typeof FormData !== "undefined" ? FormData : null,
		Blob: typeof Blob !== "undefined" ? Blob : null
	},
	protocols: [
		"http",
		"https",
		"file",
		"blob",
		"url",
		"data"
	]
};
var utils_exports = /* @__PURE__ */ __export({
	hasBrowserEnv: () => hasBrowserEnv,
	hasStandardBrowserEnv: () => hasStandardBrowserEnv,
	hasStandardBrowserWebWorkerEnv: () => hasStandardBrowserWebWorkerEnv,
	navigator: () => _navigator,
	origin: () => origin
});
var hasBrowserEnv = typeof window !== "undefined" && typeof document !== "undefined";
var _navigator = typeof navigator === "object" && navigator || void 0;
var hasStandardBrowserEnv = hasBrowserEnv && (!_navigator || [
	"ReactNative",
	"NativeScript",
	"NS"
].indexOf(_navigator.product) < 0);
var hasStandardBrowserWebWorkerEnv = (() => {
	return typeof WorkerGlobalScope !== "undefined" && self instanceof WorkerGlobalScope && typeof self.importScripts === "function";
})();
var origin = hasBrowserEnv && window.location.href || "http://localhost";
var platform_default = {
	...utils_exports,
	...browser_default
};
function toURLEncodedForm(data, options) {
	return toFormData_default(data, new platform_default.classes.URLSearchParams(), {
		visitor: function(value, key, path, helpers) {
			if (platform_default.isNode && utils_default.isBuffer(value)) {
				this.append(key, value.toString("base64"));
				return false;
			}
			return helpers.defaultVisitor.apply(this, arguments);
		},
		...options
	});
}
function parsePropPath(name) {
	return utils_default.matchAll(/\w+|\[(\w*)]/g, name).map((match) => {
		return match[0] === "[]" ? "" : match[1] || match[0];
	});
}
function arrayToObject(arr) {
	const obj = {};
	const keys = Object.keys(arr);
	let i;
	const len = keys.length;
	let key;
	for (i = 0; i < len; i++) {
		key = keys[i];
		obj[key] = arr[key];
	}
	return obj;
}
function formDataToJSON(formData) {
	function buildPath(path, value, target, index) {
		let name = path[index++];
		if (name === "__proto__") return true;
		const isNumericKey = Number.isFinite(+name);
		const isLast = index >= path.length;
		name = !name && utils_default.isArray(target) ? target.length : name;
		if (isLast) {
			if (utils_default.hasOwnProp(target, name)) target[name] = [target[name], value];
			else target[name] = value;
			return !isNumericKey;
		}
		if (!target[name] || !utils_default.isObject(target[name])) target[name] = [];
		if (buildPath(path, value, target[name], index) && utils_default.isArray(target[name])) target[name] = arrayToObject(target[name]);
		return !isNumericKey;
	}
	if (utils_default.isFormData(formData) && utils_default.isFunction(formData.entries)) {
		const obj = {};
		utils_default.forEachEntry(formData, (name, value) => {
			buildPath(parsePropPath(name), value, obj, 0);
		});
		return obj;
	}
	return null;
}
var formDataToJSON_default = formDataToJSON;
function stringifySafely(rawValue, parser, encoder) {
	if (utils_default.isString(rawValue)) try {
		(parser || JSON.parse)(rawValue);
		return utils_default.trim(rawValue);
	} catch (e) {
		if (e.name !== "SyntaxError") throw e;
	}
	return (encoder || JSON.stringify)(rawValue);
}
var defaults = {
	transitional: transitional_default,
	adapter: [
		"xhr",
		"http",
		"fetch"
	],
	transformRequest: [function transformRequest(data, headers) {
		const contentType = headers.getContentType() || "";
		const hasJSONContentType = contentType.indexOf("application/json") > -1;
		const isObjectPayload = utils_default.isObject(data);
		if (isObjectPayload && utils_default.isHTMLForm(data)) data = new FormData(data);
		if (utils_default.isFormData(data)) return hasJSONContentType ? JSON.stringify(formDataToJSON_default(data)) : data;
		if (utils_default.isArrayBuffer(data) || utils_default.isBuffer(data) || utils_default.isStream(data) || utils_default.isFile(data) || utils_default.isBlob(data) || utils_default.isReadableStream(data)) return data;
		if (utils_default.isArrayBufferView(data)) return data.buffer;
		if (utils_default.isURLSearchParams(data)) {
			headers.setContentType("application/x-www-form-urlencoded;charset=utf-8", false);
			return data.toString();
		}
		let isFileList$1;
		if (isObjectPayload) {
			if (contentType.indexOf("application/x-www-form-urlencoded") > -1) return toURLEncodedForm(data, this.formSerializer).toString();
			if ((isFileList$1 = utils_default.isFileList(data)) || contentType.indexOf("multipart/form-data") > -1) {
				const _FormData = this.env && this.env.FormData;
				return toFormData_default(isFileList$1 ? { "files[]": data } : data, _FormData && new _FormData(), this.formSerializer);
			}
		}
		if (isObjectPayload || hasJSONContentType) {
			headers.setContentType("application/json", false);
			return stringifySafely(data);
		}
		return data;
	}],
	transformResponse: [function transformResponse(data) {
		const transitional = this.transitional || defaults.transitional;
		const forcedJSONParsing = transitional && transitional.forcedJSONParsing;
		const JSONRequested = this.responseType === "json";
		if (utils_default.isResponse(data) || utils_default.isReadableStream(data)) return data;
		if (data && utils_default.isString(data) && (forcedJSONParsing && !this.responseType || JSONRequested)) {
			const strictJSONParsing = !(transitional && transitional.silentJSONParsing) && JSONRequested;
			try {
				return JSON.parse(data, this.parseReviver);
			} catch (e) {
				if (strictJSONParsing) {
					if (e.name === "SyntaxError") throw AxiosError_default.from(e, AxiosError_default.ERR_BAD_RESPONSE, this, null, this.response);
					throw e;
				}
			}
		}
		return data;
	}],
	timeout: 0,
	xsrfCookieName: "XSRF-TOKEN",
	xsrfHeaderName: "X-XSRF-TOKEN",
	maxContentLength: -1,
	maxBodyLength: -1,
	env: {
		FormData: platform_default.classes.FormData,
		Blob: platform_default.classes.Blob
	},
	validateStatus: function validateStatus(status) {
		return status >= 200 && status < 300;
	},
	headers: { common: {
		"Accept": "application/json, text/plain, */*",
		"Content-Type": void 0
	} }
};
utils_default.forEach([
	"delete",
	"get",
	"head",
	"post",
	"put",
	"patch"
], (method) => {
	defaults.headers[method] = {};
});
var defaults_default = defaults;
var ignoreDuplicateOf = utils_default.toObjectSet([
	"age",
	"authorization",
	"content-length",
	"content-type",
	"etag",
	"expires",
	"from",
	"host",
	"if-modified-since",
	"if-unmodified-since",
	"last-modified",
	"location",
	"max-forwards",
	"proxy-authorization",
	"referer",
	"retry-after",
	"user-agent"
]);
var parseHeaders_default = (rawHeaders) => {
	const parsed = {};
	let key;
	let val;
	let i;
	rawHeaders && rawHeaders.split("\n").forEach(function parser(line) {
		i = line.indexOf(":");
		key = line.substring(0, i).trim().toLowerCase();
		val = line.substring(i + 1).trim();
		if (!key || parsed[key] && ignoreDuplicateOf[key]) return;
		if (key === "set-cookie") if (parsed[key]) parsed[key].push(val);
		else parsed[key] = [val];
		else parsed[key] = parsed[key] ? parsed[key] + ", " + val : val;
	});
	return parsed;
};
var $internals = Symbol("internals");
function normalizeHeader(header) {
	return header && String(header).trim().toLowerCase();
}
function normalizeValue(value) {
	if (value === false || value == null) return value;
	return utils_default.isArray(value) ? value.map(normalizeValue) : String(value);
}
function parseTokens(str) {
	const tokens = Object.create(null);
	const tokensRE = /([^\s,;=]+)\s*(?:=\s*([^,;]+))?/g;
	let match;
	while (match = tokensRE.exec(str)) tokens[match[1]] = match[2];
	return tokens;
}
var isValidHeaderName = (str) => /^[-_a-zA-Z0-9^`|~,!#$%&'*+.]+$/.test(str.trim());
function matchHeaderValue(context, value, header, filter, isHeaderNameFilter) {
	if (utils_default.isFunction(filter)) return filter.call(this, value, header);
	if (isHeaderNameFilter) value = header;
	if (!utils_default.isString(value)) return;
	if (utils_default.isString(filter)) return value.indexOf(filter) !== -1;
	if (utils_default.isRegExp(filter)) return filter.test(value);
}
function formatHeader(header) {
	return header.trim().toLowerCase().replace(/([a-z\d])(\w*)/g, (w, char, str) => {
		return char.toUpperCase() + str;
	});
}
function buildAccessors(obj, header) {
	const accessorName = utils_default.toCamelCase(" " + header);
	[
		"get",
		"set",
		"has"
	].forEach((methodName) => {
		Object.defineProperty(obj, methodName + accessorName, {
			value: function(arg1, arg2, arg3) {
				return this[methodName].call(this, header, arg1, arg2, arg3);
			},
			configurable: true
		});
	});
}
var AxiosHeaders = class {
	constructor(headers) {
		headers && this.set(headers);
	}
	set(header, valueOrRewrite, rewrite) {
		const self$1 = this;
		function setHeader(_value, _header, _rewrite) {
			const lHeader = normalizeHeader(_header);
			if (!lHeader) throw new Error("header name must be a non-empty string");
			const key = utils_default.findKey(self$1, lHeader);
			if (!key || self$1[key] === void 0 || _rewrite === true || _rewrite === void 0 && self$1[key] !== false) self$1[key || _header] = normalizeValue(_value);
		}
		const setHeaders = (headers, _rewrite) => utils_default.forEach(headers, (_value, _header) => setHeader(_value, _header, _rewrite));
		if (utils_default.isPlainObject(header) || header instanceof this.constructor) setHeaders(header, valueOrRewrite);
		else if (utils_default.isString(header) && (header = header.trim()) && !isValidHeaderName(header)) setHeaders(parseHeaders_default(header), valueOrRewrite);
		else if (utils_default.isObject(header) && utils_default.isIterable(header)) {
			let obj = {}, dest, key;
			for (const entry of header) {
				if (!utils_default.isArray(entry)) throw TypeError("Object iterator must return a key-value pair");
				obj[key = entry[0]] = (dest = obj[key]) ? utils_default.isArray(dest) ? [...dest, entry[1]] : [dest, entry[1]] : entry[1];
			}
			setHeaders(obj, valueOrRewrite);
		} else header != null && setHeader(valueOrRewrite, header, rewrite);
		return this;
	}
	get(header, parser) {
		header = normalizeHeader(header);
		if (header) {
			const key = utils_default.findKey(this, header);
			if (key) {
				const value = this[key];
				if (!parser) return value;
				if (parser === true) return parseTokens(value);
				if (utils_default.isFunction(parser)) return parser.call(this, value, key);
				if (utils_default.isRegExp(parser)) return parser.exec(value);
				throw new TypeError("parser must be boolean|regexp|function");
			}
		}
	}
	has(header, matcher) {
		header = normalizeHeader(header);
		if (header) {
			const key = utils_default.findKey(this, header);
			return !!(key && this[key] !== void 0 && (!matcher || matchHeaderValue(this, this[key], key, matcher)));
		}
		return false;
	}
	delete(header, matcher) {
		const self$1 = this;
		let deleted = false;
		function deleteHeader(_header) {
			_header = normalizeHeader(_header);
			if (_header) {
				const key = utils_default.findKey(self$1, _header);
				if (key && (!matcher || matchHeaderValue(self$1, self$1[key], key, matcher))) {
					delete self$1[key];
					deleted = true;
				}
			}
		}
		if (utils_default.isArray(header)) header.forEach(deleteHeader);
		else deleteHeader(header);
		return deleted;
	}
	clear(matcher) {
		const keys = Object.keys(this);
		let i = keys.length;
		let deleted = false;
		while (i--) {
			const key = keys[i];
			if (!matcher || matchHeaderValue(this, this[key], key, matcher, true)) {
				delete this[key];
				deleted = true;
			}
		}
		return deleted;
	}
	normalize(format) {
		const self$1 = this;
		const headers = {};
		utils_default.forEach(this, (value, header) => {
			const key = utils_default.findKey(headers, header);
			if (key) {
				self$1[key] = normalizeValue(value);
				delete self$1[header];
				return;
			}
			const normalized = format ? formatHeader(header) : String(header).trim();
			if (normalized !== header) delete self$1[header];
			self$1[normalized] = normalizeValue(value);
			headers[normalized] = true;
		});
		return this;
	}
	concat(...targets) {
		return this.constructor.concat(this, ...targets);
	}
	toJSON(asStrings) {
		const obj = Object.create(null);
		utils_default.forEach(this, (value, header) => {
			value != null && value !== false && (obj[header] = asStrings && utils_default.isArray(value) ? value.join(", ") : value);
		});
		return obj;
	}
	[Symbol.iterator]() {
		return Object.entries(this.toJSON())[Symbol.iterator]();
	}
	toString() {
		return Object.entries(this.toJSON()).map(([header, value]) => header + ": " + value).join("\n");
	}
	getSetCookie() {
		return this.get("set-cookie") || [];
	}
	get [Symbol.toStringTag]() {
		return "AxiosHeaders";
	}
	static from(thing) {
		return thing instanceof this ? thing : new this(thing);
	}
	static concat(first, ...targets) {
		const computed = new this(first);
		targets.forEach((target) => computed.set(target));
		return computed;
	}
	static accessor(header) {
		const accessors = (this[$internals] = this[$internals] = { accessors: {} }).accessors;
		const prototype$2 = this.prototype;
		function defineAccessor(_header) {
			const lHeader = normalizeHeader(_header);
			if (!accessors[lHeader]) {
				buildAccessors(prototype$2, _header);
				accessors[lHeader] = true;
			}
		}
		utils_default.isArray(header) ? header.forEach(defineAccessor) : defineAccessor(header);
		return this;
	}
};
AxiosHeaders.accessor([
	"Content-Type",
	"Content-Length",
	"Accept",
	"Accept-Encoding",
	"User-Agent",
	"Authorization"
]);
utils_default.reduceDescriptors(AxiosHeaders.prototype, ({ value }, key) => {
	let mapped = key[0].toUpperCase() + key.slice(1);
	return {
		get: () => value,
		set(headerValue) {
			this[mapped] = headerValue;
		}
	};
});
utils_default.freezeMethods(AxiosHeaders);
var AxiosHeaders_default = AxiosHeaders;
function transformData(fns, response) {
	const config = this || defaults_default;
	const context = response || config;
	const headers = AxiosHeaders_default.from(context.headers);
	let data = context.data;
	utils_default.forEach(fns, function transform(fn) {
		data = fn.call(config, data, headers.normalize(), response ? response.status : void 0);
	});
	headers.normalize();
	return data;
}
function isCancel(value) {
	return !!(value && value.__CANCEL__);
}
function CanceledError(message, config, request) {
	AxiosError_default.call(this, message == null ? "canceled" : message, AxiosError_default.ERR_CANCELED, config, request);
	this.name = "CanceledError";
}
utils_default.inherits(CanceledError, AxiosError_default, { __CANCEL__: true });
var CanceledError_default = CanceledError;
function settle(resolve, reject, response) {
	const validateStatus = response.config.validateStatus;
	if (!response.status || !validateStatus || validateStatus(response.status)) resolve(response);
	else reject(new AxiosError_default("Request failed with status code " + response.status, [AxiosError_default.ERR_BAD_REQUEST, AxiosError_default.ERR_BAD_RESPONSE][Math.floor(response.status / 100) - 4], response.config, response.request, response));
}
function parseProtocol(url) {
	const match = /^([-+\w]{1,25})(:?\/\/|:)/.exec(url);
	return match && match[1] || "";
}
function speedometer(samplesCount, min) {
	samplesCount = samplesCount || 10;
	const bytes = new Array(samplesCount);
	const timestamps = new Array(samplesCount);
	let head = 0;
	let tail = 0;
	let firstSampleTS;
	min = min !== void 0 ? min : 1e3;
	return function push(chunkLength) {
		const now = Date.now();
		const startedAt = timestamps[tail];
		if (!firstSampleTS) firstSampleTS = now;
		bytes[head] = chunkLength;
		timestamps[head] = now;
		let i = tail;
		let bytesCount = 0;
		while (i !== head) {
			bytesCount += bytes[i++];
			i = i % samplesCount;
		}
		head = (head + 1) % samplesCount;
		if (head === tail) tail = (tail + 1) % samplesCount;
		if (now - firstSampleTS < min) return;
		const passed = startedAt && now - startedAt;
		return passed ? Math.round(bytesCount * 1e3 / passed) : void 0;
	};
}
var speedometer_default = speedometer;
function throttle(fn, freq) {
	let timestamp = 0;
	let threshold = 1e3 / freq;
	let lastArgs;
	let timer;
	const invoke = (args, now = Date.now()) => {
		timestamp = now;
		lastArgs = null;
		if (timer) {
			clearTimeout(timer);
			timer = null;
		}
		fn(...args);
	};
	const throttled = (...args) => {
		const now = Date.now();
		const passed = now - timestamp;
		if (passed >= threshold) invoke(args, now);
		else {
			lastArgs = args;
			if (!timer) timer = setTimeout(() => {
				timer = null;
				invoke(lastArgs);
			}, threshold - passed);
		}
	};
	const flush = () => lastArgs && invoke(lastArgs);
	return [throttled, flush];
}
var throttle_default = throttle;
const progressEventReducer = (listener, isDownloadStream, freq = 3) => {
	let bytesNotified = 0;
	const _speedometer = speedometer_default(50, 250);
	return throttle_default((e) => {
		const loaded = e.loaded;
		const total = e.lengthComputable ? e.total : void 0;
		const progressBytes = loaded - bytesNotified;
		const rate = _speedometer(progressBytes);
		const inRange = loaded <= total;
		bytesNotified = loaded;
		listener({
			loaded,
			total,
			progress: total ? loaded / total : void 0,
			bytes: progressBytes,
			rate: rate ? rate : void 0,
			estimated: rate && total && inRange ? (total - loaded) / rate : void 0,
			event: e,
			lengthComputable: total != null,
			[isDownloadStream ? "download" : "upload"]: true
		});
	}, freq);
};
const progressEventDecorator = (total, throttled) => {
	const lengthComputable = total != null;
	return [(loaded) => throttled[0]({
		lengthComputable,
		total,
		loaded
	}), throttled[1]];
};
const asyncDecorator = (fn) => (...args) => utils_default.asap(() => fn(...args));
var isURLSameOrigin_default = platform_default.hasStandardBrowserEnv ? ((origin$1, isMSIE) => (url) => {
	url = new URL(url, platform_default.origin);
	return origin$1.protocol === url.protocol && origin$1.host === url.host && (isMSIE || origin$1.port === url.port);
})(new URL(platform_default.origin), platform_default.navigator && /(msie|trident)/i.test(platform_default.navigator.userAgent)) : () => true;
var cookies_default = platform_default.hasStandardBrowserEnv ? {
	write(name, value, expires, path, domain, secure) {
		const cookie = [name + "=" + encodeURIComponent(value)];
		utils_default.isNumber(expires) && cookie.push("expires=" + new Date(expires).toGMTString());
		utils_default.isString(path) && cookie.push("path=" + path);
		utils_default.isString(domain) && cookie.push("domain=" + domain);
		secure === true && cookie.push("secure");
		document.cookie = cookie.join("; ");
	},
	read(name) {
		const match = document.cookie.match(/* @__PURE__ */ new RegExp("(^|;\\s*)(" + name + ")=([^;]*)"));
		return match ? decodeURIComponent(match[3]) : null;
	},
	remove(name) {
		this.write(name, "", Date.now() - 864e5);
	}
} : {
	write() {},
	read() {
		return null;
	},
	remove() {}
};
function isAbsoluteURL(url) {
	return /^([a-z][a-z\d+\-.]*:)?\/\//i.test(url);
}
function combineURLs(baseURL, relativeURL) {
	return relativeURL ? baseURL.replace(/\/?\/$/, "") + "/" + relativeURL.replace(/^\/+/, "") : baseURL;
}
function buildFullPath(baseURL, requestedURL, allowAbsoluteUrls) {
	let isRelativeUrl = !isAbsoluteURL(requestedURL);
	if (baseURL && (isRelativeUrl || allowAbsoluteUrls == false)) return combineURLs(baseURL, requestedURL);
	return requestedURL;
}
var headersToObject = (thing) => thing instanceof AxiosHeaders_default ? { ...thing } : thing;
function mergeConfig(config1, config2) {
	config2 = config2 || {};
	const config = {};
	function getMergedValue(target, source, prop, caseless) {
		if (utils_default.isPlainObject(target) && utils_default.isPlainObject(source)) return utils_default.merge.call({ caseless }, target, source);
		else if (utils_default.isPlainObject(source)) return utils_default.merge({}, source);
		else if (utils_default.isArray(source)) return source.slice();
		return source;
	}
	function mergeDeepProperties(a, b, prop, caseless) {
		if (!utils_default.isUndefined(b)) return getMergedValue(a, b, prop, caseless);
		else if (!utils_default.isUndefined(a)) return getMergedValue(void 0, a, prop, caseless);
	}
	function valueFromConfig2(a, b) {
		if (!utils_default.isUndefined(b)) return getMergedValue(void 0, b);
	}
	function defaultToConfig2(a, b) {
		if (!utils_default.isUndefined(b)) return getMergedValue(void 0, b);
		else if (!utils_default.isUndefined(a)) return getMergedValue(void 0, a);
	}
	function mergeDirectKeys(a, b, prop) {
		if (prop in config2) return getMergedValue(a, b);
		else if (prop in config1) return getMergedValue(void 0, a);
	}
	const mergeMap = {
		url: valueFromConfig2,
		method: valueFromConfig2,
		data: valueFromConfig2,
		baseURL: defaultToConfig2,
		transformRequest: defaultToConfig2,
		transformResponse: defaultToConfig2,
		paramsSerializer: defaultToConfig2,
		timeout: defaultToConfig2,
		timeoutMessage: defaultToConfig2,
		withCredentials: defaultToConfig2,
		withXSRFToken: defaultToConfig2,
		adapter: defaultToConfig2,
		responseType: defaultToConfig2,
		xsrfCookieName: defaultToConfig2,
		xsrfHeaderName: defaultToConfig2,
		onUploadProgress: defaultToConfig2,
		onDownloadProgress: defaultToConfig2,
		decompress: defaultToConfig2,
		maxContentLength: defaultToConfig2,
		maxBodyLength: defaultToConfig2,
		beforeRedirect: defaultToConfig2,
		transport: defaultToConfig2,
		httpAgent: defaultToConfig2,
		httpsAgent: defaultToConfig2,
		cancelToken: defaultToConfig2,
		socketPath: defaultToConfig2,
		responseEncoding: defaultToConfig2,
		validateStatus: mergeDirectKeys,
		headers: (a, b, prop) => mergeDeepProperties(headersToObject(a), headersToObject(b), prop, true)
	};
	utils_default.forEach(Object.keys({
		...config1,
		...config2
	}), function computeConfigValue(prop) {
		const merge$1 = mergeMap[prop] || mergeDeepProperties;
		const configValue = merge$1(config1[prop], config2[prop], prop);
		utils_default.isUndefined(configValue) && merge$1 !== mergeDirectKeys || (config[prop] = configValue);
	});
	return config;
}
var resolveConfig_default = (config) => {
	const newConfig = mergeConfig({}, config);
	let { data, withXSRFToken, xsrfHeaderName, xsrfCookieName, headers, auth } = newConfig;
	newConfig.headers = headers = AxiosHeaders_default.from(headers);
	newConfig.url = buildURL(buildFullPath(newConfig.baseURL, newConfig.url, newConfig.allowAbsoluteUrls), config.params, config.paramsSerializer);
	if (auth) headers.set("Authorization", "Basic " + btoa((auth.username || "") + ":" + (auth.password ? unescape(encodeURIComponent(auth.password)) : "")));
	if (utils_default.isFormData(data)) {
		if (platform_default.hasStandardBrowserEnv || platform_default.hasStandardBrowserWebWorkerEnv) headers.setContentType(void 0);
		else if (utils_default.isFunction(data.getHeaders)) {
			const formHeaders = data.getHeaders();
			const allowedHeaders = ["content-type", "content-length"];
			Object.entries(formHeaders).forEach(([key, val]) => {
				if (allowedHeaders.includes(key.toLowerCase())) headers.set(key, val);
			});
		}
	}
	if (platform_default.hasStandardBrowserEnv) {
		withXSRFToken && utils_default.isFunction(withXSRFToken) && (withXSRFToken = withXSRFToken(newConfig));
		if (withXSRFToken || withXSRFToken !== false && isURLSameOrigin_default(newConfig.url)) {
			const xsrfValue = xsrfHeaderName && xsrfCookieName && cookies_default.read(xsrfCookieName);
			if (xsrfValue) headers.set(xsrfHeaderName, xsrfValue);
		}
	}
	return newConfig;
};
var xhr_default = typeof XMLHttpRequest !== "undefined" && function(config) {
	return new Promise(function dispatchXhrRequest(resolve, reject) {
		const _config = resolveConfig_default(config);
		let requestData = _config.data;
		const requestHeaders = AxiosHeaders_default.from(_config.headers).normalize();
		let { responseType, onUploadProgress, onDownloadProgress } = _config;
		let onCanceled;
		let uploadThrottled, downloadThrottled;
		let flushUpload, flushDownload;
		function done() {
			flushUpload && flushUpload();
			flushDownload && flushDownload();
			_config.cancelToken && _config.cancelToken.unsubscribe(onCanceled);
			_config.signal && _config.signal.removeEventListener("abort", onCanceled);
		}
		let request = new XMLHttpRequest();
		request.open(_config.method.toUpperCase(), _config.url, true);
		request.timeout = _config.timeout;
		function onloadend() {
			if (!request) return;
			const responseHeaders = AxiosHeaders_default.from("getAllResponseHeaders" in request && request.getAllResponseHeaders());
			settle(function _resolve(value) {
				resolve(value);
				done();
			}, function _reject(err) {
				reject(err);
				done();
			}, {
				data: !responseType || responseType === "text" || responseType === "json" ? request.responseText : request.response,
				status: request.status,
				statusText: request.statusText,
				headers: responseHeaders,
				config,
				request
			});
			request = null;
		}
		if ("onloadend" in request) request.onloadend = onloadend;
		else request.onreadystatechange = function handleLoad() {
			if (!request || request.readyState !== 4) return;
			if (request.status === 0 && !(request.responseURL && request.responseURL.indexOf("file:") === 0)) return;
			setTimeout(onloadend);
		};
		request.onabort = function handleAbort() {
			if (!request) return;
			reject(new AxiosError_default("Request aborted", AxiosError_default.ECONNABORTED, config, request));
			request = null;
		};
		request.onerror = function handleError(event) {
			const err = new AxiosError_default(event && event.message ? event.message : "Network Error", AxiosError_default.ERR_NETWORK, config, request);
			err.event = event || null;
			reject(err);
			request = null;
		};
		request.ontimeout = function handleTimeout() {
			let timeoutErrorMessage = _config.timeout ? "timeout of " + _config.timeout + "ms exceeded" : "timeout exceeded";
			const transitional = _config.transitional || transitional_default;
			if (_config.timeoutErrorMessage) timeoutErrorMessage = _config.timeoutErrorMessage;
			reject(new AxiosError_default(timeoutErrorMessage, transitional.clarifyTimeoutError ? AxiosError_default.ETIMEDOUT : AxiosError_default.ECONNABORTED, config, request));
			request = null;
		};
		requestData === void 0 && requestHeaders.setContentType(null);
		if ("setRequestHeader" in request) utils_default.forEach(requestHeaders.toJSON(), function setRequestHeader(val, key) {
			request.setRequestHeader(key, val);
		});
		if (!utils_default.isUndefined(_config.withCredentials)) request.withCredentials = !!_config.withCredentials;
		if (responseType && responseType !== "json") request.responseType = _config.responseType;
		if (onDownloadProgress) {
			[downloadThrottled, flushDownload] = progressEventReducer(onDownloadProgress, true);
			request.addEventListener("progress", downloadThrottled);
		}
		if (onUploadProgress && request.upload) {
			[uploadThrottled, flushUpload] = progressEventReducer(onUploadProgress);
			request.upload.addEventListener("progress", uploadThrottled);
			request.upload.addEventListener("loadend", flushUpload);
		}
		if (_config.cancelToken || _config.signal) {
			onCanceled = (cancel) => {
				if (!request) return;
				reject(!cancel || cancel.type ? new CanceledError_default(null, config, request) : cancel);
				request.abort();
				request = null;
			};
			_config.cancelToken && _config.cancelToken.subscribe(onCanceled);
			if (_config.signal) _config.signal.aborted ? onCanceled() : _config.signal.addEventListener("abort", onCanceled);
		}
		const protocol = parseProtocol(_config.url);
		if (protocol && platform_default.protocols.indexOf(protocol) === -1) {
			reject(new AxiosError_default("Unsupported protocol " + protocol + ":", AxiosError_default.ERR_BAD_REQUEST, config));
			return;
		}
		request.send(requestData || null);
	});
};
var composeSignals = (signals, timeout) => {
	const { length } = signals = signals ? signals.filter(Boolean) : [];
	if (timeout || length) {
		let controller = new AbortController();
		let aborted;
		const onabort = function(reason) {
			if (!aborted) {
				aborted = true;
				unsubscribe();
				const err = reason instanceof Error ? reason : this.reason;
				controller.abort(err instanceof AxiosError_default ? err : new CanceledError_default(err instanceof Error ? err.message : err));
			}
		};
		let timer = timeout && setTimeout(() => {
			timer = null;
			onabort(new AxiosError_default(`timeout ${timeout} of ms exceeded`, AxiosError_default.ETIMEDOUT));
		}, timeout);
		const unsubscribe = () => {
			if (signals) {
				timer && clearTimeout(timer);
				timer = null;
				signals.forEach((signal$1) => {
					signal$1.unsubscribe ? signal$1.unsubscribe(onabort) : signal$1.removeEventListener("abort", onabort);
				});
				signals = null;
			}
		};
		signals.forEach((signal$1) => signal$1.addEventListener("abort", onabort));
		const { signal } = controller;
		signal.unsubscribe = () => utils_default.asap(unsubscribe);
		return signal;
	}
};
var composeSignals_default = composeSignals;
const streamChunk = function* (chunk, chunkSize) {
	let len = chunk.byteLength;
	if (!chunkSize || len < chunkSize) {
		yield chunk;
		return;
	}
	let pos = 0;
	let end;
	while (pos < len) {
		end = pos + chunkSize;
		yield chunk.slice(pos, end);
		pos = end;
	}
};
const readBytes = async function* (iterable, chunkSize) {
	for await (const chunk of readStream(iterable)) yield* streamChunk(chunk, chunkSize);
};
var readStream = async function* (stream) {
	if (stream[Symbol.asyncIterator]) {
		yield* stream;
		return;
	}
	const reader = stream.getReader();
	try {
		for (;;) {
			const { done, value } = await reader.read();
			if (done) break;
			yield value;
		}
	} finally {
		await reader.cancel();
	}
};
const trackStream = (stream, chunkSize, onProgress, onFinish) => {
	const iterator$1 = readBytes(stream, chunkSize);
	let bytes = 0;
	let done;
	let _onFinish = (e) => {
		if (!done) {
			done = true;
			onFinish && onFinish(e);
		}
	};
	return new ReadableStream({
		async pull(controller) {
			try {
				const { done: done$1, value } = await iterator$1.next();
				if (done$1) {
					_onFinish();
					controller.close();
					return;
				}
				let len = value.byteLength;
				if (onProgress) onProgress(bytes += len);
				controller.enqueue(new Uint8Array(value));
			} catch (err) {
				_onFinish(err);
				throw err;
			}
		},
		cancel(reason) {
			_onFinish(reason);
			return iterator$1.return();
		}
	}, { highWaterMark: 2 });
};
var DEFAULT_CHUNK_SIZE = 64 * 1024;
var { isFunction } = utils_default;
var globalFetchAPI = (({ Request, Response }) => ({
	Request,
	Response
}))(utils_default.global);
var { ReadableStream: ReadableStream$1, TextEncoder } = utils_default.global;
var test = (fn, ...args) => {
	try {
		return !!fn(...args);
	} catch (e) {
		return false;
	}
};
var factory = (env) => {
	env = utils_default.merge.call({ skipUndefined: true }, globalFetchAPI, env);
	const { fetch: envFetch, Request, Response } = env;
	const isFetchSupported = envFetch ? isFunction(envFetch) : typeof fetch === "function";
	const isRequestSupported = isFunction(Request);
	const isResponseSupported = isFunction(Response);
	if (!isFetchSupported) return false;
	const isReadableStreamSupported = isFetchSupported && isFunction(ReadableStream$1);
	const encodeText = isFetchSupported && (typeof TextEncoder === "function" ? ((encoder) => (str) => encoder.encode(str))(new TextEncoder()) : async (str) => new Uint8Array(await new Request(str).arrayBuffer()));
	const supportsRequestStream = isRequestSupported && isReadableStreamSupported && test(() => {
		let duplexAccessed = false;
		const hasContentType = new Request(platform_default.origin, {
			body: new ReadableStream$1(),
			method: "POST",
			get duplex() {
				duplexAccessed = true;
				return "half";
			}
		}).headers.has("Content-Type");
		return duplexAccessed && !hasContentType;
	});
	const supportsResponseStream = isResponseSupported && isReadableStreamSupported && test(() => utils_default.isReadableStream(new Response("").body));
	const resolvers = { stream: supportsResponseStream && ((res) => res.body) };
	isFetchSupported && [
		"text",
		"arrayBuffer",
		"blob",
		"formData",
		"stream"
	].forEach((type) => {
		!resolvers[type] && (resolvers[type] = (res, config) => {
			let method = res && res[type];
			if (method) return method.call(res);
			throw new AxiosError_default(`Response type '${type}' is not supported`, AxiosError_default.ERR_NOT_SUPPORT, config);
		});
	});
	const getBodyLength = async (body) => {
		if (body == null) return 0;
		if (utils_default.isBlob(body)) return body.size;
		if (utils_default.isSpecCompliantForm(body)) return (await new Request(platform_default.origin, {
			method: "POST",
			body
		}).arrayBuffer()).byteLength;
		if (utils_default.isArrayBufferView(body) || utils_default.isArrayBuffer(body)) return body.byteLength;
		if (utils_default.isURLSearchParams(body)) body = body + "";
		if (utils_default.isString(body)) return (await encodeText(body)).byteLength;
	};
	const resolveBodyLength = async (headers, body) => {
		const length = utils_default.toFiniteNumber(headers.getContentLength());
		return length == null ? getBodyLength(body) : length;
	};
	return async (config) => {
		let { url, method, data, signal, cancelToken, timeout, onDownloadProgress, onUploadProgress, responseType, headers, withCredentials = "same-origin", fetchOptions } = resolveConfig_default(config);
		let _fetch = envFetch || fetch;
		responseType = responseType ? (responseType + "").toLowerCase() : "text";
		let composedSignal = composeSignals_default([signal, cancelToken && cancelToken.toAbortSignal()], timeout);
		let request = null;
		const unsubscribe = composedSignal && composedSignal.unsubscribe && (() => {
			composedSignal.unsubscribe();
		});
		let requestContentLength;
		try {
			if (onUploadProgress && supportsRequestStream && method !== "get" && method !== "head" && (requestContentLength = await resolveBodyLength(headers, data)) !== 0) {
				let _request = new Request(url, {
					method: "POST",
					body: data,
					duplex: "half"
				});
				let contentTypeHeader;
				if (utils_default.isFormData(data) && (contentTypeHeader = _request.headers.get("content-type"))) headers.setContentType(contentTypeHeader);
				if (_request.body) {
					const [onProgress, flush] = progressEventDecorator(requestContentLength, progressEventReducer(asyncDecorator(onUploadProgress)));
					data = trackStream(_request.body, DEFAULT_CHUNK_SIZE, onProgress, flush);
				}
			}
			if (!utils_default.isString(withCredentials)) withCredentials = withCredentials ? "include" : "omit";
			const isCredentialsSupported = isRequestSupported && "credentials" in Request.prototype;
			const resolvedOptions = {
				...fetchOptions,
				signal: composedSignal,
				method: method.toUpperCase(),
				headers: headers.normalize().toJSON(),
				body: data,
				duplex: "half",
				credentials: isCredentialsSupported ? withCredentials : void 0
			};
			request = isRequestSupported && new Request(url, resolvedOptions);
			let response = await (isRequestSupported ? _fetch(request, fetchOptions) : _fetch(url, resolvedOptions));
			const isStreamResponse = supportsResponseStream && (responseType === "stream" || responseType === "response");
			if (supportsResponseStream && (onDownloadProgress || isStreamResponse && unsubscribe)) {
				const options = {};
				[
					"status",
					"statusText",
					"headers"
				].forEach((prop) => {
					options[prop] = response[prop];
				});
				const responseContentLength = utils_default.toFiniteNumber(response.headers.get("content-length"));
				const [onProgress, flush] = onDownloadProgress && progressEventDecorator(responseContentLength, progressEventReducer(asyncDecorator(onDownloadProgress), true)) || [];
				response = new Response(trackStream(response.body, DEFAULT_CHUNK_SIZE, onProgress, () => {
					flush && flush();
					unsubscribe && unsubscribe();
				}), options);
			}
			responseType = responseType || "text";
			let responseData = await resolvers[utils_default.findKey(resolvers, responseType) || "text"](response, config);
			!isStreamResponse && unsubscribe && unsubscribe();
			return await new Promise((resolve, reject) => {
				settle(resolve, reject, {
					data: responseData,
					headers: AxiosHeaders_default.from(response.headers),
					status: response.status,
					statusText: response.statusText,
					config,
					request
				});
			});
		} catch (err) {
			unsubscribe && unsubscribe();
			if (err && err.name === "TypeError" && /Load failed|fetch/i.test(err.message)) throw Object.assign(new AxiosError_default("Network Error", AxiosError_default.ERR_NETWORK, config, request), { cause: err.cause || err });
			throw AxiosError_default.from(err, err && err.code, config, request);
		}
	};
};
var seedCache = /* @__PURE__ */ new Map();
const getFetch = (config) => {
	let env = config ? config.env : {};
	const { fetch: fetch$1, Request, Response } = env;
	const seeds = [
		Request,
		Response,
		fetch$1
	];
	let i = seeds.length, seed, target, map = seedCache;
	while (i--) {
		seed = seeds[i];
		target = map.get(seed);
		target === void 0 && map.set(seed, target = i ? /* @__PURE__ */ new Map() : factory(env));
		map = target;
	}
	return target;
};
getFetch();
var knownAdapters = {
	http: null,
	xhr: xhr_default,
	fetch: { get: getFetch }
};
utils_default.forEach(knownAdapters, (fn, value) => {
	if (fn) {
		try {
			Object.defineProperty(fn, "name", { value });
		} catch (e) {}
		Object.defineProperty(fn, "adapterName", { value });
	}
});
var renderReason = (reason) => `- ${reason}`;
var isResolvedHandle = (adapter$1) => utils_default.isFunction(adapter$1) || adapter$1 === null || adapter$1 === false;
var adapters_default = {
	getAdapter: (adapters, config) => {
		adapters = utils_default.isArray(adapters) ? adapters : [adapters];
		const { length } = adapters;
		let nameOrAdapter;
		let adapter$1;
		const rejectedReasons = {};
		for (let i = 0; i < length; i++) {
			nameOrAdapter = adapters[i];
			let id;
			adapter$1 = nameOrAdapter;
			if (!isResolvedHandle(nameOrAdapter)) {
				adapter$1 = knownAdapters[(id = String(nameOrAdapter)).toLowerCase()];
				if (adapter$1 === void 0) throw new AxiosError_default(`Unknown adapter '${id}'`);
			}
			if (adapter$1 && (utils_default.isFunction(adapter$1) || (adapter$1 = adapter$1.get(config)))) break;
			rejectedReasons[id || "#" + i] = adapter$1;
		}
		if (!adapter$1) {
			const reasons = Object.entries(rejectedReasons).map(([id, state]) => `adapter ${id} ` + (state === false ? "is not supported by the environment" : "is not available in the build"));
			throw new AxiosError_default(`There is no suitable adapter to dispatch the request ` + (length ? reasons.length > 1 ? "since :\n" + reasons.map(renderReason).join("\n") : " " + renderReason(reasons[0]) : "as no adapter specified"), "ERR_NOT_SUPPORT");
		}
		return adapter$1;
	},
	adapters: knownAdapters
};
function throwIfCancellationRequested(config) {
	if (config.cancelToken) config.cancelToken.throwIfRequested();
	if (config.signal && config.signal.aborted) throw new CanceledError_default(null, config);
}
function dispatchRequest(config) {
	throwIfCancellationRequested(config);
	config.headers = AxiosHeaders_default.from(config.headers);
	config.data = transformData.call(config, config.transformRequest);
	if ([
		"post",
		"put",
		"patch"
	].indexOf(config.method) !== -1) config.headers.setContentType("application/x-www-form-urlencoded", false);
	return adapters_default.getAdapter(config.adapter || defaults_default.adapter, config)(config).then(function onAdapterResolution(response) {
		throwIfCancellationRequested(config);
		response.data = transformData.call(config, config.transformResponse, response);
		response.headers = AxiosHeaders_default.from(response.headers);
		return response;
	}, function onAdapterRejection(reason) {
		if (!isCancel(reason)) {
			throwIfCancellationRequested(config);
			if (reason && reason.response) {
				reason.response.data = transformData.call(config, config.transformResponse, reason.response);
				reason.response.headers = AxiosHeaders_default.from(reason.response.headers);
			}
		}
		return Promise.reject(reason);
	});
}
const VERSION = "1.12.2";
var validators$1 = {};
[
	"object",
	"boolean",
	"number",
	"function",
	"string",
	"symbol"
].forEach((type, i) => {
	validators$1[type] = function validator(thing) {
		return typeof thing === type || "a" + (i < 1 ? "n " : " ") + type;
	};
});
var deprecatedWarnings = {};
validators$1.transitional = function transitional(validator, version, message) {
	function formatMessage(opt, desc) {
		return "[Axios v" + VERSION + "] Transitional option '" + opt + "'" + desc + (message ? ". " + message : "");
	}
	return (value, opt, opts) => {
		if (validator === false) throw new AxiosError_default(formatMessage(opt, " has been removed" + (version ? " in " + version : "")), AxiosError_default.ERR_DEPRECATED);
		if (version && !deprecatedWarnings[opt]) {
			deprecatedWarnings[opt] = true;
			console.warn(formatMessage(opt, " has been deprecated since v" + version + " and will be removed in the near future"));
		}
		return validator ? validator(value, opt, opts) : true;
	};
};
validators$1.spelling = function spelling(correctSpelling) {
	return (value, opt) => {
		console.warn(`${opt} is likely a misspelling of ${correctSpelling}`);
		return true;
	};
};
function assertOptions(options, schema, allowUnknown) {
	if (typeof options !== "object") throw new AxiosError_default("options must be an object", AxiosError_default.ERR_BAD_OPTION_VALUE);
	const keys = Object.keys(options);
	let i = keys.length;
	while (i-- > 0) {
		const opt = keys[i];
		const validator = schema[opt];
		if (validator) {
			const value = options[opt];
			const result = value === void 0 || validator(value, opt, options);
			if (result !== true) throw new AxiosError_default("option " + opt + " must be " + result, AxiosError_default.ERR_BAD_OPTION_VALUE);
			continue;
		}
		if (allowUnknown !== true) throw new AxiosError_default("Unknown option " + opt, AxiosError_default.ERR_BAD_OPTION);
	}
}
var validator_default = {
	assertOptions,
	validators: validators$1
};
var validators = validator_default.validators;
var Axios = class {
	constructor(instanceConfig) {
		this.defaults = instanceConfig || {};
		this.interceptors = {
			request: new InterceptorManager_default(),
			response: new InterceptorManager_default()
		};
	}
	async request(configOrUrl, config) {
		try {
			return await this._request(configOrUrl, config);
		} catch (err) {
			if (err instanceof Error) {
				let dummy = {};
				Error.captureStackTrace ? Error.captureStackTrace(dummy) : dummy = /* @__PURE__ */ new Error();
				const stack = dummy.stack ? dummy.stack.replace(/^.+\n/, "") : "";
				try {
					if (!err.stack) err.stack = stack;
					else if (stack && !String(err.stack).endsWith(stack.replace(/^.+\n.+\n/, ""))) err.stack += "\n" + stack;
				} catch (e) {}
			}
			throw err;
		}
	}
	_request(configOrUrl, config) {
		if (typeof configOrUrl === "string") {
			config = config || {};
			config.url = configOrUrl;
		} else config = configOrUrl || {};
		config = mergeConfig(this.defaults, config);
		const { transitional, paramsSerializer, headers } = config;
		if (transitional !== void 0) validator_default.assertOptions(transitional, {
			silentJSONParsing: validators.transitional(validators.boolean),
			forcedJSONParsing: validators.transitional(validators.boolean),
			clarifyTimeoutError: validators.transitional(validators.boolean)
		}, false);
		if (paramsSerializer != null) if (utils_default.isFunction(paramsSerializer)) config.paramsSerializer = { serialize: paramsSerializer };
		else validator_default.assertOptions(paramsSerializer, {
			encode: validators.function,
			serialize: validators.function
		}, true);
		if (config.allowAbsoluteUrls !== void 0) {} else if (this.defaults.allowAbsoluteUrls !== void 0) config.allowAbsoluteUrls = this.defaults.allowAbsoluteUrls;
		else config.allowAbsoluteUrls = true;
		validator_default.assertOptions(config, {
			baseUrl: validators.spelling("baseURL"),
			withXsrfToken: validators.spelling("withXSRFToken")
		}, true);
		config.method = (config.method || this.defaults.method || "get").toLowerCase();
		let contextHeaders = headers && utils_default.merge(headers.common, headers[config.method]);
		headers && utils_default.forEach([
			"delete",
			"get",
			"head",
			"post",
			"put",
			"patch",
			"common"
		], (method) => {
			delete headers[method];
		});
		config.headers = AxiosHeaders_default.concat(contextHeaders, headers);
		const requestInterceptorChain = [];
		let synchronousRequestInterceptors = true;
		this.interceptors.request.forEach(function unshiftRequestInterceptors(interceptor) {
			if (typeof interceptor.runWhen === "function" && interceptor.runWhen(config) === false) return;
			synchronousRequestInterceptors = synchronousRequestInterceptors && interceptor.synchronous;
			requestInterceptorChain.unshift(interceptor.fulfilled, interceptor.rejected);
		});
		const responseInterceptorChain = [];
		this.interceptors.response.forEach(function pushResponseInterceptors(interceptor) {
			responseInterceptorChain.push(interceptor.fulfilled, interceptor.rejected);
		});
		let promise;
		let i = 0;
		let len;
		if (!synchronousRequestInterceptors) {
			const chain = [dispatchRequest.bind(this), void 0];
			chain.unshift(...requestInterceptorChain);
			chain.push(...responseInterceptorChain);
			len = chain.length;
			promise = Promise.resolve(config);
			while (i < len) promise = promise.then(chain[i++], chain[i++]);
			return promise;
		}
		len = requestInterceptorChain.length;
		let newConfig = config;
		while (i < len) {
			const onFulfilled = requestInterceptorChain[i++];
			const onRejected = requestInterceptorChain[i++];
			try {
				newConfig = onFulfilled(newConfig);
			} catch (error) {
				onRejected.call(this, error);
				break;
			}
		}
		try {
			promise = dispatchRequest.call(this, newConfig);
		} catch (error) {
			return Promise.reject(error);
		}
		i = 0;
		len = responseInterceptorChain.length;
		while (i < len) promise = promise.then(responseInterceptorChain[i++], responseInterceptorChain[i++]);
		return promise;
	}
	getUri(config) {
		config = mergeConfig(this.defaults, config);
		return buildURL(buildFullPath(config.baseURL, config.url, config.allowAbsoluteUrls), config.params, config.paramsSerializer);
	}
};
utils_default.forEach([
	"delete",
	"get",
	"head",
	"options"
], function forEachMethodNoData(method) {
	Axios.prototype[method] = function(url, config) {
		return this.request(mergeConfig(config || {}, {
			method,
			url,
			data: (config || {}).data
		}));
	};
});
utils_default.forEach([
	"post",
	"put",
	"patch"
], function forEachMethodWithData(method) {
	function generateHTTPMethod(isForm) {
		return function httpMethod(url, data, config) {
			return this.request(mergeConfig(config || {}, {
				method,
				headers: isForm ? { "Content-Type": "multipart/form-data" } : {},
				url,
				data
			}));
		};
	}
	Axios.prototype[method] = generateHTTPMethod();
	Axios.prototype[method + "Form"] = generateHTTPMethod(true);
});
var Axios_default = Axios;
var CancelToken_default = class CancelToken {
	constructor(executor) {
		if (typeof executor !== "function") throw new TypeError("executor must be a function.");
		let resolvePromise;
		this.promise = new Promise(function promiseExecutor(resolve) {
			resolvePromise = resolve;
		});
		const token = this;
		this.promise.then((cancel) => {
			if (!token._listeners) return;
			let i = token._listeners.length;
			while (i-- > 0) token._listeners[i](cancel);
			token._listeners = null;
		});
		this.promise.then = (onfulfilled) => {
			let _resolve;
			const promise = new Promise((resolve) => {
				token.subscribe(resolve);
				_resolve = resolve;
			}).then(onfulfilled);
			promise.cancel = function reject() {
				token.unsubscribe(_resolve);
			};
			return promise;
		};
		executor(function cancel(message, config, request) {
			if (token.reason) return;
			token.reason = new CanceledError_default(message, config, request);
			resolvePromise(token.reason);
		});
	}
	throwIfRequested() {
		if (this.reason) throw this.reason;
	}
	subscribe(listener) {
		if (this.reason) {
			listener(this.reason);
			return;
		}
		if (this._listeners) this._listeners.push(listener);
		else this._listeners = [listener];
	}
	unsubscribe(listener) {
		if (!this._listeners) return;
		const index = this._listeners.indexOf(listener);
		if (index !== -1) this._listeners.splice(index, 1);
	}
	toAbortSignal() {
		const controller = new AbortController();
		const abort = (err) => {
			controller.abort(err);
		};
		this.subscribe(abort);
		controller.signal.unsubscribe = () => this.unsubscribe(abort);
		return controller.signal;
	}
	static source() {
		let cancel;
		return {
			token: new CancelToken(function executor(c) {
				cancel = c;
			}),
			cancel
		};
	}
};
function spread(callback) {
	return function wrap(arr) {
		return callback.apply(null, arr);
	};
}
function isAxiosError(payload) {
	return utils_default.isObject(payload) && payload.isAxiosError === true;
}
var HttpStatusCode = {
	Continue: 100,
	SwitchingProtocols: 101,
	Processing: 102,
	EarlyHints: 103,
	Ok: 200,
	Created: 201,
	Accepted: 202,
	NonAuthoritativeInformation: 203,
	NoContent: 204,
	ResetContent: 205,
	PartialContent: 206,
	MultiStatus: 207,
	AlreadyReported: 208,
	ImUsed: 226,
	MultipleChoices: 300,
	MovedPermanently: 301,
	Found: 302,
	SeeOther: 303,
	NotModified: 304,
	UseProxy: 305,
	Unused: 306,
	TemporaryRedirect: 307,
	PermanentRedirect: 308,
	BadRequest: 400,
	Unauthorized: 401,
	PaymentRequired: 402,
	Forbidden: 403,
	NotFound: 404,
	MethodNotAllowed: 405,
	NotAcceptable: 406,
	ProxyAuthenticationRequired: 407,
	RequestTimeout: 408,
	Conflict: 409,
	Gone: 410,
	LengthRequired: 411,
	PreconditionFailed: 412,
	PayloadTooLarge: 413,
	UriTooLong: 414,
	UnsupportedMediaType: 415,
	RangeNotSatisfiable: 416,
	ExpectationFailed: 417,
	ImATeapot: 418,
	MisdirectedRequest: 421,
	UnprocessableEntity: 422,
	Locked: 423,
	FailedDependency: 424,
	TooEarly: 425,
	UpgradeRequired: 426,
	PreconditionRequired: 428,
	TooManyRequests: 429,
	RequestHeaderFieldsTooLarge: 431,
	UnavailableForLegalReasons: 451,
	InternalServerError: 500,
	NotImplemented: 501,
	BadGateway: 502,
	ServiceUnavailable: 503,
	GatewayTimeout: 504,
	HttpVersionNotSupported: 505,
	VariantAlsoNegotiates: 506,
	InsufficientStorage: 507,
	LoopDetected: 508,
	NotExtended: 510,
	NetworkAuthenticationRequired: 511
};
Object.entries(HttpStatusCode).forEach(([key, value]) => {
	HttpStatusCode[value] = key;
});
var HttpStatusCode_default = HttpStatusCode;
function createInstance(defaultConfig) {
	const context = new Axios_default(defaultConfig);
	const instance = bind(Axios_default.prototype.request, context);
	utils_default.extend(instance, Axios_default.prototype, context, { allOwnKeys: true });
	utils_default.extend(instance, context, null, { allOwnKeys: true });
	instance.create = function create(instanceConfig) {
		return createInstance(mergeConfig(defaultConfig, instanceConfig));
	};
	return instance;
}
var axios = createInstance(defaults_default);
axios.Axios = Axios_default;
axios.CanceledError = CanceledError_default;
axios.CancelToken = CancelToken_default;
axios.isCancel = isCancel;
axios.VERSION = VERSION;
axios.toFormData = toFormData_default;
axios.AxiosError = AxiosError_default;
axios.Cancel = axios.CanceledError;
axios.all = function all(promises) {
	return Promise.all(promises);
};
axios.spread = spread;
axios.isAxiosError = isAxiosError;
axios.mergeConfig = mergeConfig;
axios.AxiosHeaders = AxiosHeaders_default;
axios.formToJSON = (thing) => formDataToJSON_default(utils_default.isHTMLForm(thing) ? new FormData(thing) : thing);
axios.getAdapter = adapters_default.getAdapter;
axios.HttpStatusCode = HttpStatusCode_default;
axios.default = axios;
var axios_default = axios;
export { require_pusher as n, axios_default as t };
