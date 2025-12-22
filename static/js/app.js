const { createApp } = Vue;

// i18n Translations
const translations = {
    zh: {
        title: '医学影像AHA分型评估系统',
        login: {
            title: '用户登录',
            placeholder: '请输入您的用户名',
            button: '登录'
        },
        mode: {
            excel: 'Excel模式',
            custom: '自定义输入模式',
            switchConfirm: '切换模式将清空当前未保存的内容，确定继续吗？'
        },
        control: {
            welcome: '欢迎',
            progress: '进度',
            searchPlaceholder: '按条码号跳转',
            jump: '跳转',
            export: '导出结果'
        },
        patient: {
            title: '病人信息',
            barcode: '条码号',
            findings: '检查所见'
        },
        custom: {
            title: '自定义检查所见',
            placeholder: '请输入检查所见内容...',
            history: '历史自定义评估',
            selectLoad: '-- 选择加载 --',
            submitSuccess: '✅ 自定义评估已保存: {id}',
            emptyFindings: '请先输入检查所见内容',
            clearForm: '清空表单'
        },
        assessment: {
            title: '医生评估',
            ahaClassification: 'AHA分型评估',
            leftSide: '左侧评估',
            rightSide: '右侧评估',
            usefulness: '有用性评估',
            leftUsefulness: '左侧有用性',
            rightUsefulness: '右侧有用性',
            timeSpent: '当前用时',
            submitted: '已提交',
            submit: '提交',
            resubmit: '重新提交',
            nextPatient: '下一个病人'
        },
        ai: {
            title: 'AI 推理',
            start: '启动AI分析',
            loading: '推理中...',
            inference: '推理过程',
            classification: 'AHA分型结果',
            leftSide: '左侧',
            rightSide: '右侧',
            none: '无',
            placeholder: '点击 "启动AI分析" 获取结果。'
        },
        messages: {
            loginSuccess: '登录成功,已加载用户 {username} 的进度。',
            submitSuccess: '✅ 提交成功！用时: {time}秒',
            submitWarning: '⚠️ 请先提交当前病人的评估！',
            submitBeforeJump: '⚠️ 请先提交当前病人的评估再跳转！',
            jumpSuccess: '已成功跳转到条码号: {barcode}',
            nextPatient: '已加载下一位病人。',
            exportStart: '正在生成导出文件...',
            exportSuccess: '文件已开始下载。',
            noFindings: '当前病人没有检查所见信息。',
            enterBarcode: '请输入要跳转的条码号。',
            emptyUsername: '用户名不能为空'
        }
    },
    en: {
        title: 'Medical Imaging AHA Classification System',
        login: {
            title: 'User Login',
            placeholder: 'Enter your username',
            button: 'Login'
        },
        mode: {
            excel: 'Excel Mode',
            custom: 'Custom Input Mode',
            switchConfirm: 'Switching modes will clear unsaved content. Continue?'
        },
        control: {
            welcome: 'Welcome',
            progress: 'Progress',
            searchPlaceholder: 'Jump to barcode',
            jump: 'Jump',
            export: 'Export Results'
        },
        patient: {
            title: 'Patient Information',
            barcode: 'Barcode',
            findings: 'Examination Findings'
        },
        custom: {
            title: 'Custom Examination Findings',
            placeholder: 'Enter examination findings here...',
            history: 'Custom Evaluation History',
            selectLoad: '-- Select to load --',
            submitSuccess: '✅ Custom evaluation saved: {id}',
            emptyFindings: 'Please enter examination findings first',
            clearForm: 'Clear Form'
        },
        assessment: {
            title: 'Doctor Assessment',
            ahaClassification: 'AHA Classification',
            leftSide: 'Left Side',
            rightSide: 'Right Side',
            usefulness: 'Usefulness Assessment',
            leftUsefulness: 'Left Usefulness',
            rightUsefulness: 'Right Usefulness',
            timeSpent: 'Time Spent',
            submitted: 'Submitted',
            submit: 'Submit',
            resubmit: 'Resubmit',
            nextPatient: 'Next Patient'
        },
        ai: {
            title: 'AI Inference',
            start: 'Start AI Analysis',
            loading: 'Analyzing...',
            inference: 'Inference Process',
            classification: 'AHA Classification Results',
            leftSide: 'Left',
            rightSide: 'Right',
            none: 'None',
            placeholder: 'Click "Start AI Analysis" to get results.'
        },
        messages: {
            loginSuccess: 'Login successful, user {username} progress loaded.',
            submitSuccess: '✅ Submitted successfully! Time: {time}s',
            submitWarning: '⚠️ Please submit the current patient assessment first!',
            submitBeforeJump: '⚠️ Please submit current assessment before jumping!',
            jumpSuccess: 'Successfully jumped to barcode: {barcode}',
            nextPatient: 'Next patient loaded.',
            exportStart: 'Generating export file...',
            exportSuccess: 'File download started.',
            noFindings: 'Current patient has no examination findings.',
            enterBarcode: 'Please enter a barcode to jump to.',
            emptyUsername: 'Username cannot be empty'
        }
    }
};

createApp({
    data() {
        return {
            // Language
            language: localStorage.getItem('language') || 'zh',

            // State
            loggedIn: false,
            username: '',
            loginError: '',
            statusMessage: '',
            statusClass: '',

            // Mode
            mode: 'excel',  // 'excel' or 'custom'

            // Patient Data
            patientIndex: 0,
            totalPatients: 0,
            currentPatient: {},

            // Custom Mode
            customFindings: '',
            customHistory: [],
            selectedCustomId: null,

            // Assessment
            leftAssessment: 1,
            rightAssessment: 1,
            leftConsistency: 0,
            rightConsistency: 0,
            timeSpent: 0,

            // Submission tracking
            hasSubmitted: false,
            hasModified: false,

            // Timer
            startTime: null,
            currentTime: 0,
            timerInterval: null,

            // UI
            barcodeSearch: '',
            romanLabels: { 1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII', 8: 'VIII' },

            // AI
            aiLoading: false,
            aiResult: '',
            aiResultParsed: null
        };
    },
    computed: {
        t() {
            return translations[this.language];
        }
    },
    methods: {
        // --- Language Switching ---
        switchLanguage(lang) {
            this.language = lang;
            localStorage.setItem('language', lang);
            document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en';
        },

        // --- Translation Helper ---
        translate(key, params = {}) {
            let text = this.t.messages[key] || key;
            Object.keys(params).forEach(param => {
                text = text.replace(`{${param}}`, params[param]);
            });
            return text;
        },

        // --- API Calls ---
        async apiCall(endpoint, method = 'POST', body = {}) {
            try {
                const response = await axios({
                    method: method,
                    url: `http://127.0.0.1:5001/api/${endpoint}`,
                    data: body,
                    responseType: endpoint === 'export' ? 'blob' : 'json'
                });
                return response.data;
            } catch (error) {
                const errorMessage = error.response?.data?.error || error.message || 'Unknown error';
                this.showStatus(errorMessage, 'error');
                throw new Error(errorMessage);
            }
        },

        // --- Authentication ---
        async login() {
            if (!this.username.trim()) {
                this.loginError = this.translate('emptyUsername');
                return;
            }
            this.loginError = '';
            try {
                const data = await this.apiCall('login', 'POST', { username: this.username });
                this.updatePatientData(data);
                this.loggedIn = true;
                this.showStatus(this.translate('loginSuccess', { username: this.username }), 'success');
            } catch (error) {
                // error is already displayed by apiCall
            }
        },

        // --- Data Handling ---
        updatePatientData(data) {
            this.currentPatient = {
                barcode: data.barcode,
                findings: data.findings
            };
            this.patientIndex = data.index;
            this.totalPatients = data.total;

            // Set sliders to loaded values
            this.leftAssessment = data.labels.left_assessment;
            this.rightAssessment = data.labels.right_assessment;
            this.leftConsistency = data.labels.left_usefulness;
            this.rightConsistency = data.labels.right_usefulness;
            this.timeSpent = data.labels.time_spent || 0;

            // Reset submission status
            this.hasSubmitted = false;
            this.hasModified = false;

            // Reset AI result for new patient
            this.aiResult = '';
            this.aiResultParsed = null;

            // Start the timer
            this.startTimer();
        },

        // --- Timer Functions ---
        startTimer() {
            // Clear any existing timer
            if (this.timerInterval) {
                clearInterval(this.timerInterval);
            }

            // Set start time
            this.startTime = Date.now();
            this.currentTime = 0;

            // Update timer every 100ms for smooth display
            this.timerInterval = setInterval(() => {
                this.currentTime = (Date.now() - this.startTime) / 1000;
            }, 100);
        },

        stopTimer() {
            if (this.timerInterval) {
                clearInterval(this.timerInterval);
                this.timerInterval = null;
            }
        },

        getFormattedTime() {
            const seconds = Math.floor(this.currentTime);
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
        },

        // --- Navigation ---
        async nextPatient() {
            // 检查是否已提交
            if (!this.hasSubmitted) {
                this.showStatus(this.translate('submitWarning'), 'error');
                return;
            }

            try {
                const data = await this.apiCall('patient/navigate', 'POST', { username: this.username, direction: 'next' });
                this.updatePatientData(data);
                this.showStatus(this.translate('nextPatient'), 'success');
            } catch (error) {
                // error message is shown by apiCall
            }
        },

        async jumpToPatient() {
            if (!this.barcodeSearch.trim()) {
                this.showStatus(this.translate('enterBarcode'), 'error');
                return;
            }

            // 检查是否已提交
            if (!this.hasSubmitted) {
                this.showStatus(this.translate('submitBeforeJump'), 'error');
                return;
            }

            try {
                const data = await this.apiCall('patient/jump', 'POST', { username: this.username, barcode: this.barcodeSearch });
                this.updatePatientData(data);
                this.showStatus(this.translate('jumpSuccess', { barcode: this.barcodeSearch }), 'success');
                this.barcodeSearch = '';
            } catch (error) {
                // error message is shown by apiCall
            }
        },

        // --- Actions ---
        async submitEvaluation() {
            try {
                const payload = {
                    username: this.username,
                    labels: {
                        left_assessment: this.leftAssessment,
                        right_assessment: this.rightAssessment,
                        left_usefulness: this.leftConsistency,
                        right_usefulness: this.rightConsistency,
                    }
                };
                const response = await this.apiCall('submit', 'POST', payload);
                this.timeSpent = response.time_spent;
                this.hasSubmitted = true;
                this.hasModified = false;
                this.showStatus(this.translate('submitSuccess', { time: response.time_spent.toFixed(2) }), 'success');
            } catch (error) {
                // error message is shown by apiCall
            }
        },

        async exportResults() {
            try {
                this.showStatus(this.translate('exportStart'), 'success');
                const blob = await this.apiCall('export', 'POST', { username: this.username });
                const url = window.URL.createObjectURL(new Blob([blob]));
                const link = document.createElement('a');
                link.href = url;
                const filename = `${this.username}_export_${Date.now()}.xlsx`;
                link.setAttribute('download', filename);
                document.body.appendChild(link);
                link.click();
                link.remove();
                this.showStatus(this.translate('exportSuccess'), 'success');
            } catch (error) {
                // error message is shown by apiCall
            }
        },

        async runAI() {
            const findings = this.mode === 'excel'
                ? this.currentPatient.findings
                : this.customFindings;

            if (!findings || !findings.trim()) {
                this.showStatus(
                    this.mode === 'excel'
                        ? this.translate('noFindings')
                        : this.t.custom.emptyFindings,
                    'error'
                );
                return;
            }

            this.aiLoading = true;
            this.aiResult = '';
            this.aiResultParsed = null;
            try {
                const res = await this.apiCall('infer', 'POST', { findings: findings });
                if (res.error) throw new Error(res.error);

                // backend returns { result: '...', validated: bool, data: {...} }
                this.aiResult = res.result || '';

                // If backend successfully validated the response, use the validated data
                if (res.validated && res.data) {
                    this.aiResultParsed = res.data;

                    // Show warning if there was partial recovery
                    if (res.warning) {
                        console.warn('AI响应验证警告:', res.warning);
                    }
                } else {
                    // Backend validation failed, try client-side parsing as fallback
                    console.warn('后端验证失败，尝试前端解析:', res.error);

                    try {
                        this.aiResultParsed = JSON.parse(this.aiResult);
                    } catch (e) {
                        // If not valid JSON, try to extract JSON from markdown code blocks
                        const jsonMatch = this.aiResult.match(/```(?:json)?\s*(\{[\s\S]*?\})\s*```/);
                        if (jsonMatch) {
                            try {
                                this.aiResultParsed = JSON.parse(jsonMatch[1]);
                            } catch (e2) {
                                // Failed to parse, will display raw result
                                console.warn('前端JSON解析也失败，显示原始文本');
                            }
                        }
                    }
                }
            } catch (error) {
                this.aiResult = `AI ${this.language === 'zh' ? '推理失败' : 'inference failed'}: ${error.message}`;
            } finally {
                this.aiLoading = false;
            }
        },

        // --- Custom Mode Methods ---
        async switchMode(newMode) {
            // Warn if unsaved changes
            if (this.mode === 'excel' && !this.hasSubmitted) {
                if (!confirm(this.t.mode.switchConfirm)) return;
            }
            if (this.mode === 'custom' && this.customFindings && !this.hasSubmitted) {
                if (!confirm(this.t.mode.switchConfirm)) return;
            }

            try {
                // Call backend to switch mode
                await this.apiCall('mode/switch', 'POST', {
                    username: this.username,
                    mode: newMode
                });

                this.mode = newMode;
                this.hasSubmitted = false;

                // Load custom history if switching to custom mode
                if (newMode === 'custom') {
                    await this.loadCustomHistory();
                    this.startTimer();  // Start timer for custom mode
                }
            } catch (error) {
                // error message is shown by apiCall
            }
        },

        async loadCustomHistory() {
            try {
                const data = await this.apiCall('custom/list', 'POST', {
                    username: this.username
                });
                this.customHistory = data.evaluations;
            } catch (error) {
                // error message is shown by apiCall
            }
        },

        async loadCustomEvaluation() {
            if (!this.selectedCustomId) return;

            try {
                const data = await this.apiCall('custom/load', 'POST', {
                    username: this.username,
                    custom_id: this.selectedCustomId
                });

                // Populate form with loaded data
                this.customFindings = data.findings;
                this.leftAssessment = data.labels.left_assessment;
                this.rightAssessment = data.labels.right_assessment;
                this.leftConsistency = data.labels.left_usefulness;
                this.rightConsistency = data.labels.right_usefulness;
                this.aiResult = data.ai_result || '';
                this.aiResultParsed = null;

                // Try to parse AI result if it exists
                if (this.aiResult) {
                    try {
                        this.aiResultParsed = JSON.parse(this.aiResult);
                    } catch (e) {
                        // Not JSON, that's okay
                    }
                }

                this.hasSubmitted = false;
            } catch (error) {
                // error message is shown by apiCall
            }
        },

        async submitCustomEvaluation() {
            if (!this.customFindings.trim()) {
                this.showStatus(this.t.custom.emptyFindings, 'error');
                return;
            }

            try {
                const payload = {
                    username: this.username,
                    findings: this.customFindings,
                    labels: {
                        left_assessment: this.leftAssessment,
                        right_assessment: this.rightAssessment,
                        left_usefulness: this.leftConsistency,
                        right_usefulness: this.rightConsistency
                    },
                    ai_result: this.aiResult
                };

                const response = await this.apiCall('custom/submit', 'POST', payload);
                this.hasSubmitted = true;
                this.showStatus(this.translate('custom.submitSuccess', { id: response.custom_id }), 'success');

                // Refresh history
                await this.loadCustomHistory();

                // Clear form
                this.clearCustomForm();
            } catch (error) {
                // error message is shown by apiCall
            }
        },

        clearCustomForm() {
            this.customFindings = '';
            this.selectedCustomId = null;
            this.leftAssessment = 1;
            this.rightAssessment = 1;
            this.leftConsistency = 0;
            this.rightConsistency = 0;
            this.aiResult = '';
            this.aiResultParsed = null;
            this.hasSubmitted = false;
            this.startTimer();  // Restart timer
        },

        // --- UI Helpers ---
        showStatus(message, type = 'error') {
            this.statusMessage = message;
            this.statusClass = type; // 'success' or 'error'
            setTimeout(() => {
                this.statusMessage = '';
            }, 4000);
        }
    },
    mounted() {
        // Set initial language for document
        document.documentElement.lang = this.language === 'zh' ? 'zh-CN' : 'en';
    },
    beforeUnmount() {
        this.stopTimer();
    },
    watch: {
        username(newUser) {
            // Optional: save username to localStorage
            // localStorage.setItem('medical-ass-user', newUser);
        }
    }
}).mount('#app');
