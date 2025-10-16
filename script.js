async function loadDataset(datasetKey) {
    const config = datasetsConfig[datasetKey];
    const loader = document.getElementById(config.elements.loader);
    const applyBtn = document.querySelector(`.apply-btn[data-dataset="${datasetKey}"]`);
    loader.innerHTML = `Carregando ${datasetKey.replace(/-/g, ' ')}...`;
    console.log(`Iniciando carregamento de ${datasetKey}...`);
    
    try {
        const metaResponse = await fetch(config.metadataPath);
        const metadata = await metaResponse.json();
        document.getElementById(config.elements.citation).textContent =
            metadata.chart?.citation || `Fonte: ${datasetKey}`;

        const csvResponse = await fetch(config.csvPath);
        const csvText = await csvResponse.text();

        await new Promise((resolve, reject) => {
            Papa.parse(csvText, {
                header: true,
                skipEmptyLines: true,
                complete: function(results) {
                    config.data = results.data.map(row => ({
                        Entity: String(row.Entity || 'Desconhecido').trim(),
                        Year: parseInt(row.Year) || 0,
                        ...Object.fromEntries(
                            Object.entries(config.columnMap).map(([original, newName]) => [newName, parseFloat(row[original]) || 0])
                        )
                    })).filter(row => row.Entity !== 'Desconhecido' && row.Year >= config.minYear && row.Year <= config.maxYear);

                    console.log(`✅ Dados de ${datasetKey} processados: ${config.data.length} linhas válidas.`);
                    initializeFilters(datasetKey);
                    if (applyBtn) applyBtn.disabled = false;
                    loader.style.display = 'none';
                    resolve();
                },
                error: reject
            });
        });
    } catch (error) {
        console.error(`❌ Erro ao carregar dataset ${datasetKey}:`, error);
        loader.innerHTML = `Erro: ${error.message}`;
    }
}
