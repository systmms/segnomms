/* SegnoMMS Visual Review Suite - Shared JavaScript */

// Global review state
const ReviewSuite = {
    currentView: 'dashboard',
    testResults: {},
    visualTests: [],
    currentDiffIndex: 0
};

// Initialize the review suite
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    loadTestResults();
    setupInteractivity();
    initializeTooltips();
});

// Navigation handling
function initializeNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const view = item.dataset.view;
            switchView(view);
        });
    });
}

function switchView(view) {
    // Update active nav item
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.view === view);
    });
    
    // Show/hide content sections
    document.querySelectorAll('.view-section').forEach(section => {
        section.style.display = section.id === `${view}-view` ? 'block' : 'none';
    });
    
    ReviewSuite.currentView = view;
    
    // View-specific initialization
    if (view === 'visual-diffs' && ReviewSuite.visualTests.length > 0) {
        showDiff(0);
    }
}

// Test results loading
async function loadTestResults() {
    try {
        // Load test results JSON if available
        const response = await fetch('data/test_results.json');
        if (response.ok) {
            ReviewSuite.testResults = await response.json();
            updateTestSummary();
        }
    } catch (error) {
        console.log('No test results found or error loading:', error);
    }
}

function updateTestSummary() {
    const results = ReviewSuite.testResults;
    
    // Update stat cards
    updateStatCard('tests-passed', results.passed || 0);
    updateStatCard('tests-failed', results.failed || 0);
    updateStatCard('tests-total', results.total || 0);
    updateStatCard('coverage', results.coverage ? `${results.coverage.toFixed(1)}%` : 'N/A');
    
    // Update progress bar
    if (results.total > 0) {
        const passRate = (results.passed / results.total) * 100;
        updateProgressBar('test-progress', passRate);
    }
}

function updateStatCard(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

function updateProgressBar(id, percentage) {
    const progressBar = document.getElementById(id);
    if (progressBar) {
        const fill = progressBar.querySelector('.progress-fill');
        fill.style.width = `${percentage}%`;
        fill.textContent = `${percentage.toFixed(1)}%`;
    }
}

// Visual diff navigation
function showDiff(index) {
    if (index < 0 || index >= ReviewSuite.visualTests.length) return;
    
    ReviewSuite.currentDiffIndex = index;
    const test = ReviewSuite.visualTests[index];
    
    // Update diff display
    document.getElementById('diff-baseline').src = test.baseline;
    document.getElementById('diff-actual').src = test.actual;
    document.getElementById('diff-title').textContent = test.name;
    
    // Update navigation
    document.getElementById('diff-current').textContent = index + 1;
    document.getElementById('diff-total').textContent = ReviewSuite.visualTests.length;
    
    // Update buttons
    document.getElementById('diff-prev').disabled = index === 0;
    document.getElementById('diff-next').disabled = index === ReviewSuite.visualTests.length - 1;
}

function nextDiff() {
    showDiff(ReviewSuite.currentDiffIndex + 1);
}

function prevDiff() {
    showDiff(ReviewSuite.currentDiffIndex - 1);
}

function approveDiff() {
    const test = ReviewSuite.visualTests[ReviewSuite.currentDiffIndex];
    test.status = 'approved';
    updateDiffStatus();
    
    // Auto-advance to next diff
    if (ReviewSuite.currentDiffIndex < ReviewSuite.visualTests.length - 1) {
        nextDiff();
    }
}

function rejectDiff() {
    const test = ReviewSuite.visualTests[ReviewSuite.currentDiffIndex];
    test.status = 'rejected';
    
    // Show feedback input
    const feedback = prompt('Please describe what\'s wrong with this output:');
    if (feedback) {
        test.feedback = feedback;
    }
    
    updateDiffStatus();
}

function updateDiffStatus() {
    const approved = ReviewSuite.visualTests.filter(t => t.status === 'approved').length;
    const rejected = ReviewSuite.visualTests.filter(t => t.status === 'rejected').length;
    const pending = ReviewSuite.visualTests.length - approved - rejected;
    
    document.getElementById('diffs-approved').textContent = approved;
    document.getElementById('diffs-rejected').textContent = rejected;
    document.getElementById('diffs-pending').textContent = pending;
}

// Interactive QR module handling
function setupInteractivity() {
    // Setup click handlers for interactive QR codes
    document.addEventListener('click', function(e) {
        if (e.target.matches('.qr-module.clickable')) {
            handleModuleClick(e.target);
        }
    });
    
    // Setup hover effects
    document.addEventListener('mouseover', function(e) {
        if (e.target.matches('.qr-module')) {
            e.target.style.opacity = '0.8';
        }
    });
    
    document.addEventListener('mouseout', function(e) {
        if (e.target.matches('.qr-module')) {
            e.target.style.opacity = '1';
        }
    });
}

function handleModuleClick(module) {
    const moduleInfo = {
        row: module.dataset.row,
        col: module.dataset.col,
        type: module.dataset.type || 'unknown'
    };
    
    // Log to console
    console.log('Module clicked:', moduleInfo);
    
    // Update click log if present
    const clickLog = document.getElementById('click-log');
    if (clickLog) {
        const entry = document.createElement('div');
        entry.textContent = `[${moduleInfo.row},${moduleInfo.col}] - ${moduleInfo.type}`;
        clickLog.appendChild(entry);
        clickLog.scrollTop = clickLog.scrollHeight;
    }
}

// Tooltip initialization
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = e.target.dataset.tooltip;
    
    document.body.appendChild(tooltip);
    
    const rect = e.target.getBoundingClientRect();
    tooltip.style.left = `${rect.left + rect.width / 2}px`;
    tooltip.style.top = `${rect.top - 10}px`;
}

function hideTooltip() {
    const tooltips = document.querySelectorAll('.tooltip');
    tooltips.forEach(t => t.remove());
}

// Export functionality
function exportReview() {
    const reviewData = {
        timestamp: new Date().toISOString(),
        testResults: ReviewSuite.testResults,
        visualTests: ReviewSuite.visualTests.map(t => ({
            name: t.name,
            status: t.status || 'pending',
            feedback: t.feedback
        }))
    };
    
    const blob = new Blob([JSON.stringify(reviewData, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `review-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Filter and search functionality
function filterGallery(searchTerm) {
    const items = document.querySelectorAll('.gallery-item');
    const term = searchTerm.toLowerCase();
    
    items.forEach(item => {
        const title = item.querySelector('.gallery-item-title').textContent.toLowerCase();
        item.style.display = title.includes(term) ? 'block' : 'none';
    });
}

// Initialize search if present
const searchInput = document.getElementById('gallery-search');
if (searchInput) {
    searchInput.addEventListener('input', debounce((e) => {
        filterGallery(e.target.value);
    }, 300));
}

// Add CSS for tooltips
const style = document.createElement('style');
style.textContent = `
.tooltip {
    position: absolute;
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.875rem;
    pointer-events: none;
    transform: translate(-50%, -100%);
    white-space: nowrap;
    z-index: 1000;
}

.qr-module.clickable {
    cursor: pointer;
    transition: opacity 0.2s;
}

#click-log {
    max-height: 200px;
    overflow-y: auto;
    font-family: monospace;
    font-size: 0.875rem;
    line-height: 1.5;
}
`;
document.head.appendChild(style);

// SVG Diff Functionality
const SVGDiff = {
    modal: null,
    currentBaseline: null,
    currentActual: null,
    currentTestId: null,

    init() {
        this.createModal();
        this.loadDiff2HTML();
    },

    loadDiff2HTML() {
        // Load diff2html library if not already loaded
        if (typeof Diff2Html === 'undefined') {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/diff2html@3.4.52/bundles/js/diff2html-ui.min.js';
            script.onload = () => {
                console.log('Diff2Html loaded');
            };
            document.head.appendChild(script);
        }
    },

    createModal() {
        // Create modal HTML
        const modalHTML = `
            <div id="svg-diff-modal" class="svg-diff-modal">
                <div class="svg-diff-modal-content">
                    <div class="svg-diff-modal-header">
                        <h3 id="svg-diff-modal-title">SVG Structure Diff</h3>
                        <button class="svg-diff-close" onclick="SVGDiff.closeModal()">&times;</button>
                    </div>
                    <div class="svg-diff-tabs">
                        <button class="svg-diff-tab active" data-view="side-by-side" onclick="SVGDiff.switchView('side-by-side')">
                            Side by Side
                        </button>
                        <button class="svg-diff-tab" data-view="unified" onclick="SVGDiff.switchView('unified')">
                            Unified
                        </button>
                        <button class="svg-diff-tab" data-view="raw" onclick="SVGDiff.switchView('raw')">
                            Raw Diff
                        </button>
                    </div>
                    <div class="svg-diff-modal-body">
                        <div id="svg-diff-content" class="svg-diff-viewer"></div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.modal = document.getElementById('svg-diff-modal');
        
        // Close modal on background click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.closeModal();
            }
        });
    },

    async showDiff(testId, baselinePath, actualPath) {
        try {
            this.currentTestId = testId;
            
            // Load both SVG files
            const [baselineResponse, actualResponse] = await Promise.all([
                fetch(baselinePath),
                fetch(actualPath)
            ]);
            
            if (!baselineResponse.ok || !actualResponse.ok) {
                throw new Error('Failed to load SVG files');
            }
            
            this.currentBaseline = await baselineResponse.text();
            this.currentActual = await actualResponse.text();
            
            // Format SVGs for better diffing
            const formattedBaseline = this.formatSVG(this.currentBaseline);
            const formattedActual = this.formatSVG(this.currentActual);
            
            // Update modal title
            document.getElementById('svg-diff-modal-title').textContent = `SVG Diff: ${testId}`;
            
            // Generate and show diff
            this.generateDiff(formattedBaseline, formattedActual, 'side-by-side');
            
            // Show modal
            this.modal.classList.add('show');
            
        } catch (error) {
            console.error('Error showing SVG diff:', error);
            alert('Error loading SVG diff: ' + error.message);
        }
    },

    formatSVG(svgContent) {
        try {
            // Parse and reformat SVG for better diffing
            const parser = new DOMParser();
            const doc = parser.parseFromString(svgContent, 'image/svg+xml');
            
            if (doc.documentElement.nodeName === 'parsererror') {
                return svgContent; // Return original if parsing fails
            }
            
            // Serialize with formatting
            const serializer = new XMLSerializer();
            let formatted = serializer.serializeToString(doc);
            
            // Add line breaks for better diff visualization
            formatted = formatted
                .replace(/></g, '>\n<')
                .replace(/\s+/g, ' ')
                .trim();
            
            // Pretty print with indentation
            return this.prettifyXML(formatted);
            
        } catch (error) {
            console.warn('Error formatting SVG, using original:', error);
            return svgContent;
        }
    },

    prettifyXML(xml) {
        const PADDING = '  '; // 2 spaces for indentation
        const reg = /(>)(<)(\/*)/g;
        let pad = 0;
        
        xml = xml.replace(reg, '$1\n$2$3');
        
        return xml.split('\n').map((line) => {
            let indent = 0;
            if (line.match(/.+<\/\w[^>]*>$/)) {
                indent = 0;
            } else if (line.match(/^<\/\w/) && pad > 0) {
                pad -= 1;
            } else if (line.match(/^<\w[^>]*[^\/]>.*$/)) {
                indent = 1;
            } else {
                indent = 0;
            }
            
            const padding = PADDING.repeat(pad);
            pad += indent;
            
            return padding + line;
        }).join('\n');
    },

    generateDiff(baseline, actual, viewType) {
        if (typeof Diff2Html === 'undefined') {
            document.getElementById('svg-diff-content').innerHTML = 
                '<p>Loading diff library...</p>';
            setTimeout(() => this.generateDiff(baseline, actual, viewType), 100);
            return;
        }

        // Create unified diff format
        const unifiedDiff = this.createUnifiedDiff(baseline, actual);
        
        const configuration = {
            drawFileList: false,
            matching: 'lines',
            outputFormat: viewType === 'unified' ? 'line-by-line' : 'side-by-side',
            synchronisedScroll: true,
            highlight: true,
            fileListToggle: false,
            fileListStartVisible: false,
        };

        const diffContainer = document.getElementById('svg-diff-content');
        
        if (viewType === 'raw') {
            // Show raw diff text
            diffContainer.innerHTML = `<pre style="background: #f8f9fa; padding: 16px; border-radius: 4px; overflow: auto; max-height: 500px;"><code>${this.escapeHtml(unifiedDiff)}</code></pre>`;
        } else {
            // Use diff2html for formatted view
            const diffHtml = Diff2Html.html(unifiedDiff, configuration);
            diffContainer.innerHTML = diffHtml;
        }
    },

    createUnifiedDiff(baseline, actual) {
        // Simple diff algorithm for demonstration
        // In production, you might want to use a more sophisticated diff library
        const baselineLines = baseline.split('\n');
        const actualLines = actual.split('\n');
        
        let diff = `--- baseline.svg\n+++ actual.svg\n`;
        
        const maxLines = Math.max(baselineLines.length, actualLines.length);
        let hunkStart = 1;
        let hunkSize = maxLines;
        
        diff += `@@ -${hunkStart},${baselineLines.length} +${hunkStart},${actualLines.length} @@\n`;
        
        for (let i = 0; i < maxLines; i++) {
            const baselineLine = baselineLines[i] || '';
            const actualLine = actualLines[i] || '';
            
            if (baselineLine === actualLine) {
                diff += ` ${baselineLine}\n`;
            } else {
                if (baselineLine && i < baselineLines.length) {
                    diff += `-${baselineLine}\n`;
                }
                if (actualLine && i < actualLines.length) {
                    diff += `+${actualLine}\n`;
                }
            }
        }
        
        return diff;
    },

    switchView(viewType) {
        // Update active tab
        document.querySelectorAll('.svg-diff-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.view === viewType);
        });
        
        // Regenerate diff with new view
        if (this.currentBaseline && this.currentActual) {
            const formattedBaseline = this.formatSVG(this.currentBaseline);
            const formattedActual = this.formatSVG(this.currentActual);
            this.generateDiff(formattedBaseline, formattedActual, viewType);
        }
    },

    closeModal() {
        this.modal.classList.remove('show');
    },

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// Initialize SVG diff when page loads
document.addEventListener('DOMContentLoaded', () => {
    SVGDiff.init();
});

// Add SVG diff button to existing comparison views
function addSVGDiffButton(container, testId, baselinePath, actualPath) {
    if (!container || !testId || !baselinePath || !actualPath) return;
    
    const diffButton = document.createElement('button');
    diffButton.className = 'btn btn-secondary';
    diffButton.textContent = 'View SVG Diff';
    diffButton.onclick = () => SVGDiff.showDiff(testId, baselinePath, actualPath);
    
    // Add to container
    const buttonContainer = container.querySelector('.comparison-controls') || container;
    if (buttonContainer) {
        buttonContainer.appendChild(diffButton);
    }
}