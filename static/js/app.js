const { createApp } = Vue;

// Bilingual translations
const translations = {
    zh: {
        title: 'MRI AHA 斑块分型评估系统',
        subtitle: '基于深度学习的高分辨率颈动脉斑块分析 | Live Demo',
        examples: {
            title: '示例病例'
        },
        input: {
            title: '影像检查所见',
            placeholder: '请输入颈动脉 HRMRI 检查所见描述，包括 T1WI、T2WI、TOF 等序列的信号表现...',
            analyze: '开始分析',
            analyzing: '分析中...'
        },
        evaluation: {
            title: '评估打分',
            description: '请完成以下两步评估：先进行 AHA 分型打分，提交后再进行有用性评分',
            step1Title: 'AHA 分型打分',
            step2Title: 'AI 结果有用性评分',
            leftAHA: '左侧 AHA 分型',
            rightAHA: '右侧 AHA 分型',
            leftUsefulness: '左侧 AI 结果有用性 (1-5)',
            rightUsefulness: '右侧 AI 结果有用性 (1-5)',
            submitClassification: '提交分型打分',
            submitFinal: '提交完整评估',
            submitting: '提交中...',
            success: '评估已成功提交',
            left: '左侧',
            right: '右侧'
        },
        results: {
            title: 'AI 分析结果',
            empty: '请输入检查所见并点击"开始分析"',
            left: '左侧颈动脉',
            right: '右侧颈动脉',
            none: '无',
            reasoning: '推理过程',
            rawOutput: '原始 AI 输出',
            aiResult: 'AI 结果'
        },
        footer: {
            text: 'MRI AHA Plaque Classification System | Academic Live Demo | Powered by Deep Learning'
        },
        validation: {
            empty: '输入为空',
            invalid: '无效预测，请检查输入为正确的HRMRI影像描述'
        },
        ahaTypes: {
            'I': 'Type I',
            'II': 'Type II',
            'III': 'Type III',
            'IV': 'Type IV',
            'V': 'Type V',
            'VI': 'Type VI',
            'VII': 'Type VII',
            'VIII': 'Type VIII'
        }
    },
    en: {
        title: 'MRI AHA Plaque Classification System',
        subtitle: 'Deep Learning-based High-Resolution Carotid Plaque Analysis | Live Demo',
        examples: {
            title: 'Example Cases'
        },
        input: {
            title: 'Imaging Findings',
            placeholder: 'Enter carotid HRMRI examination findings, including signal characteristics on T1WI, T2WI, TOF sequences...',
            analyze: 'Analyze',
            analyzing: 'Analyzing...'
        },
        evaluation: {
            title: 'Evaluation Scoring',
            description: 'Complete the two-step evaluation: First provide AHA classification scores, then rate usefulness',
            step1Title: 'AHA Classification Scoring',
            step2Title: 'AI Result Usefulness Rating',
            leftAHA: 'Left AHA Type',
            rightAHA: 'Right AHA Type',
            leftUsefulness: 'Left AI Usefulness (1-5)',
            rightUsefulness: 'Right AI Usefulness (1-5)',
            submitClassification: 'Submit Classification',
            submitFinal: 'Submit Complete Evaluation',
            submitting: 'Submitting...',
            success: 'Evaluation submitted successfully',
            left: 'Left',
            right: 'Right'
        },
        results: {
            title: 'AI Analysis Results',
            empty: 'Enter examination findings and click "Analyze"',
            left: 'Left Carotid',
            right: 'Right Carotid',
            none: 'None',
            reasoning: 'Reasoning Process',
            rawOutput: 'Raw AI Output',
            aiResult: 'AI Result'
        },
        footer: {
            text: 'MRI AHA Plaque Classification System | Academic Live Demo | Powered by Deep Learning'
        },
        validation: {
            empty: 'Input is empty',
            invalid: 'Invalid prediction, please check input is correct HRMRI imaging description'
        },
        ahaTypes: {
            'I': 'Type I',
            'II': 'Type II',
            'III': 'Type III',
            'IV': 'Type IV',
            'V': 'Type V',
            'VI': 'Type VI',
            'VII': 'Type VII',
            'VIII': 'Type VIII'
        }
    }
};

createApp({
    data() {
        return {
            // Language
            language: localStorage.getItem('language') || 'zh',

            // Prompt Version
            promptVersion: localStorage.getItem('promptVersion') || 'NP',

            // Examples
            examples: [],
            selectedExampleId: null,

            // Input
            inputFindings: '',
            validationError: '',

            // Analysis state
            isAnalyzing: false,
            hasResults: false,
            classification: { left: '', right: '' },
            reasoning: '',
            rawOutput: '',
            showRawOutput: false,

            // Evaluation state
            evaluationStep: 1, // 1: classification, 2: usefulness
            userAssessment: {
                left: 'I',
                right: 'I',
                leftUsefulness: null,
                rightUsefulness: null
            },
            isSubmitting: false,
            submissionSuccess: false,

            // Username for evaluation (stored in localStorage)
            username: localStorage.getItem('evaluationUsername') || 'demo_user_' + Math.random().toString(36).slice(2, 11)
        };
    },
    computed: {
        t() {
            return translations[this.language];
        },
        ahaTypes() {
            return Object.entries(this.t.ahaTypes).map(([value, label]) => ({ value, label }));
        }
    },
    methods: {
        // Language switching
        switchLanguage(lang) {
            this.language = lang;
            localStorage.setItem('language', lang);
            document.documentElement.lang = lang === 'zh' ? 'zh-CN' : 'en';
            this.selectedExampleId = null;
            this.loadExamples();
            this.clearResults();
        },

        // Prompt version switching
        switchPromptVersion(version) {
            this.promptVersion = version;
            localStorage.setItem('promptVersion', version);
            this.selectedExampleId = null;
            this.clearResults();
        },

        // Get AHA label by value
        getAHALabel(value) {
            return this.t.ahaTypes[value] || value;
        },

        // Load examples from API
        async loadExamples() {
            try {
                const response = await axios.get(`/api/examples?lang=${this.language}`);
                this.examples = response.data.examples;
            } catch (error) {
                console.error('Failed to load examples:', error);
                // Fallback to hardcoded examples if API fails
                this.loadFallbackExamples();
            }
        },

        // Fallback examples (in case API fails)
        loadFallbackExamples() {
            this.examples = [
                {
                    id: 'case_001',
                    title: this.language === 'zh' ? '病例 1: 双侧颈动脉粥样硬化斑块' : 'Case 1: Bilateral carotid atherosclerotic plaques',
                    findings: this.language === 'zh' ?
                        '双侧颈动脉可见斑块形成。左侧颈动脉斑块T1WI呈等信号，T2WI呈低信号，TOF呈等信号，增强扫描周边可见环形强化，提示脂质核心伴纤维帽。右侧颈动脉斑块T1WI、T2WI均呈明显低信号，提示钙化。' :
                        'Bilateral carotid arteries show plaque formation. Left carotid plaque: T1WI isointense, T2WI hypointense, TOF isointense, with peripheral enhancement on contrast-enhanced scan, suggesting lipid core with fibrous cap. Right carotid plaque: T1WI and T2WI both show marked hypointensity, suggesting calcification.'
                },
                {
                    id: 'case_002',
                    title: this.language === 'zh' ? '病例 2: 左侧颈动脉复杂斑块伴出血' : 'Case 2: Left carotid complex plaque with hemorrhage',
                    findings: this.language === 'zh' ?
                        '左侧颈动脉分叉处可见一偏心性斑块，T1WI呈高信号，T2WI信号不均，TOF呈高信号，斑块内见不规则高信号区，增强扫描显示纤维帽不完整，斑块表面可见溃疡形成。右侧颈动脉壁弥漫性增厚，无明显狭窄。' :
                        'Eccentric plaque at left carotid bifurcation: T1WI hyperintense, T2WI heterogeneous signal, TOF hyperintense, with irregular hyperintense area within plaque. Contrast-enhanced scan shows incomplete fibrous cap with surface ulceration. Right carotid artery shows diffuse wall thickening without significant stenosis.'
                },
                {
                    id: 'case_003',
                    title: this.language === 'zh' ? '病例 3: 右侧颈动脉纤维性斑块' : 'Case 3: Right carotid fibrous plaque',
                    findings: this.language === 'zh' ?
                        '右侧颈动脉可见斑块形成，T1WI呈等信号，T2WI呈等信号，TOF呈等信号，增强扫描可见明显均匀强化，无明显脂质核心或出血征象，纤维帽完整。左侧颈动脉未见明显异常。' :
                        'Right carotid artery shows plaque formation. T1WI isointense, T2WI isointense, TOF isointense. Contrast-enhanced scan shows marked homogeneous enhancement. No obvious lipid core or hemorrhage, with intact fibrous cap. Left carotid artery shows no significant abnormality.'
                },
                {
                    id: 'case_004',
                    title: this.language === 'zh' ? '病例 4: 双侧颈动脉术后改变' : 'Case 4: Post-operative bilateral carotid changes',
                    findings: this.language === 'zh' ?
                        '双侧颈动脉内膜剥脱术后改变。左侧颈动脉管腔通畅，管壁轻度增厚，未见明确斑块复发。右侧颈动脉支架植入术后，支架内通畅，未见内膜增生或再狭窄。' :
                        'Status post bilateral carotid endarterectomy. Left carotid lumen is patent with mild wall thickening, no definite plaque recurrence. Right carotid artery stent placed, stent lumen patent, no intimal hyperplasia or restenosis.'
                },
                {
                    id: 'case_005',
                    title: this.language === 'zh' ? '病例 5: 左侧近正常壁厚，右侧III型病变' : 'Case 5: Left near-normal wall, Right Type III lesion',
                    findings: this.language === 'zh' ?
                        '左侧颈动脉管壁厚度接近正常，无明显钙化。右侧颈动脉可见弥漫性内膜增厚或小的偏心性非钙化斑块，管腔轻度狭窄约30%，T1WI、T2WI信号均接近正常血管壁。' :
                        'Left carotid artery wall thickness is near-normal without calcification. Right carotid artery shows diffuse intimal thickening or small eccentric non-calcified plaque with mild stenosis (~30%). T1WI and T2WI signals are similar to normal vessel wall.'
                }
            ];
        },

        // Select an example
        selectExample(example) {
            this.selectedExampleId = example.id;
            this.inputFindings = example.findings;
            this.validationError = '';
            this.clearResults();
        },

        // Clear results
        clearResults() {
            this.hasResults = false;
            this.classification = { left: '', right: '' };
            this.reasoning = '';
            this.rawOutput = '';
            this.showRawOutput = false;
            this.evaluationStep = 1;
            this.userAssessment = {
                left: 'I',
                right: 'I',
                leftUsefulness: null,
                rightUsefulness: null
            };
            this.submissionSuccess = false;
        },

        // Analyze findings
        async analyzeFindings() {
            // Clear previous error
            this.validationError = '';
            this.submissionSuccess = false;

            // Validate input
            if (!this.inputFindings.trim()) {
                this.validationError = this.t.validation.empty;
                return;
            }

            this.isAnalyzing = true;
            this.clearResults();

            try {
                const response = await axios.post('/api/infer', {
                    findings: this.inputFindings,
                    language: this.language,
                    prompt_version: this.promptVersion
                });

                if (response.data.error) {
                    this.validationError = response.data.error;
                    return;
                }

                // Store raw output
                this.rawOutput = response.data.result || '';

                // Parse structured data if available
                if (response.data.validated && response.data.data) {
                    const data = response.data.data;

                    // Map keys based on language
                    if (this.language === 'zh') {
                        this.reasoning = data['推理过程'] || '';
                        if (data['AHA分型']) {
                            this.classification.left = data['AHA分型']['左侧'] || this.t.results.none;
                            this.classification.right = data['AHA分型']['右侧'] || this.t.results.none;
                        }
                    } else {
                        this.reasoning = data['Reasoning Process'] || '';
                        if (data['AHA Classification']) {
                            this.classification.left = data['AHA Classification']['Left'] || this.t.results.none;
                            this.classification.right = data['AHA Classification']['Right'] || this.t.results.none;
                        }
                    }

                    this.hasResults = true;
                } else {
                    // Try to parse raw output
                    this.parseRawOutput(this.rawOutput);
                }

            } catch (error) {
                const errorMsg = error.response?.data?.error || error.message;
                this.validationError = errorMsg;
            } finally {
                this.isAnalyzing = false;
            }
        },

        // Parse raw output as fallback
        parseRawOutput(raw) {
            try {
                // Try direct JSON parsing
                let parsed = JSON.parse(raw);

                if (this.language === 'zh') {
                    this.reasoning = parsed['推理过程'] || '';
                    if (parsed['AHA分型']) {
                        this.classification.left = parsed['AHA分型']['左侧'] || this.t.results.none;
                        this.classification.right = parsed['AHA分型']['右侧'] || this.t.results.none;
                    }
                } else {
                    this.reasoning = parsed['Reasoning Process'] || '';
                    if (parsed['AHA Classification']) {
                        this.classification.left = parsed['AHA Classification']['Left'] || this.t.results.none;
                        this.classification.right = parsed['AHA Classification']['Right'] || this.t.results.none;
                    }
                }

                this.hasResults = true;
            } catch (e) {
                // Try to extract JSON from markdown code block
                const jsonMatch = raw.match(/```(?:json)?\s*(\{[\s\S]*?\})\s*```/);
                if (jsonMatch) {
                    try {
                        let parsed = JSON.parse(jsonMatch[1]);

                        if (this.language === 'zh') {
                            this.reasoning = parsed['推理过程'] || '';
                            if (parsed['AHA分型']) {
                                this.classification.left = parsed['AHA分型']['左侧'] || this.t.results.none;
                                this.classification.right = parsed['AHA分型']['右侧'] || this.t.results.none;
                            }
                        } else {
                            this.reasoning = parsed['Reasoning Process'] || '';
                            if (parsed['AHA Classification']) {
                                this.classification.left = parsed['AHA Classification']['Left'] || this.t.results.none;
                                this.classification.right = parsed['AHA Classification']['Right'] || this.t.results.none;
                            }
                        }

                        this.hasResults = true;
                    } catch (e2) {
                        // Display raw output if parsing fails
                        this.hasResults = true;
                        this.reasoning = raw;
                    }
                } else {
                    // Display raw output
                    this.hasResults = true;
                    this.reasoning = raw;
                }
            }
        },

        // Submit classification (Step 1)
        submitClassification() {
            if (!this.userAssessment.left || !this.userAssessment.right) {
                return;
            }
            // Move to step 2
            this.evaluationStep = 2;
        },

        // Submit final evaluation (Step 2)
        async submitFinalEvaluation() {
            if (!this.userAssessment.leftUsefulness || !this.userAssessment.rightUsefulness) {
                return;
            }

            this.isSubmitting = true;

            try {
                // Convert numeric AHA types to Roman numerals for API
                const labels = {
                    left_assessment: this.userAssessment.left,
                    right_assessment: this.userAssessment.right,
                    left_usefulness: this.userAssessment.leftUsefulness,
                    right_usefulness: this.userAssessment.rightUsefulness
                };

                const response = await axios.post('/api/custom/submit', {
                    username: this.username,
                    findings: this.inputFindings,
                    labels: labels,
                    ai_result: this.rawOutput
                });

                if (response.data.error) {
                    alert('Error: ' + response.data.error);
                    return;
                }

                this.submissionSuccess = true;

                // Disable further editing
                this.evaluationStep = 3; // Completed state

            } catch (error) {
                console.error('Failed to submit evaluation:', error);
                alert('Failed to submit evaluation: ' + (error.response?.data?.error || error.message));
            } finally {
                this.isSubmitting = false;
            }
        }
    },
    mounted() {
        // Set initial language
        document.documentElement.lang = this.language === 'zh' ? 'zh-CN' : 'en';

        // Store username for evaluation
        localStorage.setItem('evaluationUsername', this.username);

        // Load examples
        this.loadExamples();
    }
}).mount('#app');
