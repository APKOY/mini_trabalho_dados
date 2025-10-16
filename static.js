// Configuração global (adaptada para API)
const API_BASE = '/api';
const datasetsConfig = {}; // Será populado dinamicamente

// Cores para gráficos (sem mudanças)
const chartColors = ['#00BFFF', '#ADD8E6', '#4682B4', '#87CEEB', '#6495ED', '#1E90FF', '#00CED1', '#40E0D0', '#AFEEEE', '#B0E0E6'];

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    // Detecta datasets disponíveis (via querySelector ou lista estática)
    const datasetSections = document.querySelectorAll('.dataset-section');
    datasetSections.forEach(section => {
        const datasetKey = section.id;
        datasetsConfig[datasetKey] = {
            data: [],
            filteredData: [],
            chart: null,
            mainIndicator: 'Valor', // Padrão, ajustado por dataset
            indicatorLabel: 'Valor',
            elements: {
                loader: `${datasetKey}-loader`,
                entities: `${datasetKey}-entities`,
                minYear: `${datasetKey}-minYear`,
                maxYear: `${datasetKey}-maxYear`,
                minYearDisplay: `${datasetKey}-minYearDisplay`,
                maxYearDisplay: `${datasetKey}-maxYearDisplay`,
                trendChart: `${datasetKey}-trendChart`,
                dataTable: `${datasetKey}-dataTable`,
                avgTable: `${datasetKey}-avgTable`,
                progressTable: `${datasetKey}-progressTable`,
                dataWarning: `${datasetKey}-dataWarning`,
                citation: `${datasetKey}-citation`
            }
        };
        initializeSliders(datasetKey);
        loadDatasetData(datasetKey);
    });

    // Listeners para botões de filtro
    document.querySelectorAll('.apply-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const datasetKey = this.dataset.dataset;
            applyFilters(datasetKey);
        });
    });
});

// Inicializa sliders para um dataset
function initializeSliders(datasetKey) {
    const config = datasetsConfig[datasetKey];
    const minYearSlider = document.getElementById(config.elements.minYear);
    const maxYearSlider = document.getElementById(config.elements.maxYear);
    const minYearDisplay = document.getElementById(config.elements.minYearDisplay);
    const maxYearDisplay = document.getElementById(config.elements.maxYearDisplay);

    // Valores padrão (ajuste via API se necessário)
    minYearSlider.min = 2000;
    minYearSlider.max = 2024;
    minYearSlider.value = 2000;
    minYearDisplay.textContent = 2000;
    maxYearSlider.value = 2024;
    maxYearDisplay.textContent = 2024;

    minYearSlider.addEventListener('input', function() {
        minYearDisplay.textContent = this.value;
        if (parseInt(this.value) > parseInt(maxYearSlider.value)) {
            maxYearSlider.value = this.value;
            maxYearDisplay.textContent = this.value;
        }
    });
    maxYearSlider.addEventListener('input', function() {
        maxYearDisplay.textContent = this.value;
        if (parseInt(this.value) < parseInt(minYearSlider.value)) {
            minYearSlider.value = this.value;
            minYearDisplay.textContent = this.value;
        }
    });
}

// Carrega dados e metadados para um dataset via API
async function loadDatasetData(datasetKey) {
    const config = datasetsConfig[datasetKey];
    const loader = document.getElementById(config.elements.loader);
    const applyBtn = document.querySelector(`[data-dataset="${datasetKey}"]`);

    loader.innerHTML = `Carregando ${datasetKey}...`;

    try {
        // Carrega metadados
        const metadataRes = await fetch(`${API_BASE}/metadata/${datasetKey}`);
        const metadata = await metadataRes.json();
        document.querySelector('.dataset-description').textContent = metadata.chart?.subtitle || `Descrição para ${datasetKey}`;
        document.getElementById(config.elements.citation).textContent = metadata.chart?.citation || 'Fonte não disponível';
    } catch (error) {
        loader.innerHTML = `Erro ao carregar ${datasetKey}: ${error.message}`;
        console.error(`Erro ao carregar dados do dataset ${datasetKey}:`, error);
    }
}