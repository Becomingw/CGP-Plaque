const { createApp } = Vue;

createApp({
    data() {
        return {
            // State
            loggedIn: false,
            username: '',
            loginError: '',
            statusMessage: '',
            statusClass: '',

            // Patient Data
            patientIndex: 0,
            totalPatients: 0,
            currentPatient: {},
            
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
    methods: {
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
                const errorMessage = error.response?.data?.error || error.message || '未知错误';
                this.showStatus(errorMessage, 'error');
                throw new Error(errorMessage);
            }
        },

        // --- Authentication ---
        async login() {
            if (!this.username.trim()) {
                this.loginError = '用户名不能为空';
                return;
            }
            this.loginError = '';
            try {
                const data = await this.apiCall('login', 'POST', { username: this.username });
                this.updatePatientData(data);
                this.loggedIn = true;
                this.showStatus(`登录成功，已加载用户 ${this.username} 的进度。`, 'success');
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
                this.showStatus('⚠️ 请先提交当前病人的评估！', 'error');
                return;
            }

            try {
                const data = await this.apiCall('patient/navigate', 'POST', { username: this.username, direction: 'next' });
                this.updatePatientData(data);
                this.showStatus('已加载下一位病人。', 'success');
            } catch (error) {
                // error message is shown by apiCall
            }
        },

        async jumpToPatient() {
            if (!this.barcodeSearch.trim()) {
                this.showStatus('请输入要跳转的条码号。', 'error');
                return;
            }

            // 检查是否已提交
            if (!this.hasSubmitted) {
                this.showStatus('⚠️ 请先提交当前病人的评估再跳转！', 'error');
                return;
            }

            try {
                const data = await this.apiCall('patient/jump', 'POST', { username: this.username, barcode: this.barcodeSearch });
                this.updatePatientData(data);
                this.showStatus(`已成功跳转到条码号: ${this.barcodeSearch}`, 'success');
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
                this.showStatus(`✅ 提交成功！用时: ${response.time_spent.toFixed(2)}秒`, 'success');
            } catch (error) {
                // error message is shown by apiCall
            }
        },

        async exportResults() {
            try {
                this.showStatus('正在生成导出文件...', 'success');
                const blob = await this.apiCall('export', 'POST', { username: this.username });
                const url = window.URL.createObjectURL(new Blob([blob]));
                const link = document.createElement('a');
                link.href = url;
                const filename = `${this.username}_export_${Date.now()}.xlsx`;
                link.setAttribute('download', filename);
                document.body.appendChild(link);
                link.click();
                link.remove();
                this.showStatus('文件已开始下载。', 'success');
            } catch (error) {
                // error message is shown by apiCall
            }
        },

        async runAI() {
            if (!this.currentPatient.findings) {
                this.showStatus('当前病人没有检查所见信息。', 'error');
                return;
            }
            this.aiLoading = true;
            this.aiResult = '';
            this.aiResultParsed = null;
            try {
                const res = await this.apiCall('infer', 'POST', { findings: this.currentPatient.findings });
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
                this.aiResult = `AI 推理失败: ${error.message}`;
            } finally {
                this.aiLoading = false;
            }
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
        // Clean up timer when component is destroyed
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
