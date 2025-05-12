import React, { useState } from 'react';
import './App.css';

function App() {
  const [mode, setMode] = useState(''); // 'create' or 'update'
  const [orden, setOrden] = useState('');
  const [startPrice, setStartPrice] = useState(12.0);
  const [endPrice, setEndPrice] = useState(20.0);
  const [lineNameTemplate, setLineNameTemplate] = useState('');
  const [lineItemType, setLineItemType] = useState('');
  const [priority, setPriority] = useState('');
  const [inventoryInclude, setInventoryInclude] = useState([]);
  const [inventoryExclude, setInventoryExclude] = useState([]);
  const [expectedCreative, setExpectedCreative] = useState('');
  const [deliverySettings, setDeliverySettings] = useState('IMMEDIATELY');
  const [customDate, setCustomDate] = useState('');
  const [customTime, setCustomTime] = useState('00:00');
  const [endSettings, setEndSettings] = useState('UNLIMITED');
  const [endDate, setEndDate] = useState('');
  const [endTime, setEndTime] = useState('00:00');
  const [goalUnits, setGoalUnits] = useState(100);
  const [creativeRotationType, setCreativeRotationType] = useState('EVEN');
  const [roadblockingType, setRoadblockingType] = useState('AS_MANY_AS_POSSIBLE');
  const [customTargeting, setCustomTargeting] = useState([]);
  const [placement, setPlacement] = useState('');
  const [diseño, setDiseño] = useState('');
  const [articleCount, setArticleCount] = useState('');
  const [hbDeal, setHbDeal] = useState([]);
  const [hbDealNone, setHbDealNone] = useState([]);
  const [hbDealRemove, setHbDealRemove] = useState([]);
  const [hbDealNoneRemove, setHbDealNoneRemove] = useState([]);
  const [resultado, setResultado] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [minCPM, setMinCPM] = useState(4.0); // Valor por defecto 4€
  const [startTimeOption, setStartTimeOption] = useState("IMMEDIATELY");
  const [startDate, setStartDate] = useState("");
  const [startTime, setStartTime] = useState("00:00");
  const [endTimeOption, setEndTimeOption] = useState("UNLIMITED");

  

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    setIsProcessing(true);
    setResultado('');

    let deliverySetting = deliverySettings;
    if (deliverySettings === 'CUSTOM') {
      deliverySetting = customDate;
    }

    const response = await fetch('http://127.0.0.1:5000/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        orden,
        startPrice,
        endPrice,
        line_name_template: lineNameTemplate,
        lineItemType: lineItemType.toUpperCase(),
        priority,
        inventoryInclude,
        inventoryExclude,
        expectedCreative,
        deliverySettings: deliverySetting,
        customTime: customTime,
        endSettings: endSettings,
        endDate: endDate,
        endTime: endTime,
        goalUnits: goalUnits,
        creativeRotationType: creativeRotationType,
        roadblockingType: roadblockingType,
        customTargeting,
        placement,
        diseño,
        articleCount,
        hbDeal,
        hbDealNone
      })
    });

    if (response.ok) {
      const data = await response.json();
      setResultado(data.resultado);
      console.log('Response received:', data);
    } else {
      const error = await response.text();
      console.error('Error response:', error);
      setResultado('Error al crear líneas.');
    }
    setIsProcessing(false);
  };

  const handleUpdateSubmit = async (e) => {
    e.preventDefault();
    setIsProcessing(true);
    setResultado('');

    const response = await fetch('http://127.0.0.1:5000/update', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        orden,
        hbDeal,
        hbDealNone,
        hbDealRemove,
        hbDealNoneRemove,
        lineItemType,
        priority,
        expectedCreative,
        minCPM ,
        startTimeOption,  
        startDate,       
        startTime,    
        endTimeOption,    
        endDate,          
        endTime         
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      setResultado(data.resultado);
      console.log('Response received:', data);
    } else {
      const error = await response.text();
      console.error('Error response:', error);
      setResultado('Error al actualizar líneas.');
    }
    setIsProcessing(false);
  };

  return (
    <div className="App">
      <h1>Gestor de Líneas</h1>
      {!mode && (
        <div className="buttons-app">
          <button onClick={() => setMode('create')}>Crear Líneas</button>
          <button onClick={() => setMode('update')}>Actualizar Líneas</button>
        </div>
      )}

      {mode === 'create' && (
        <form onSubmit={handleCreateSubmit}>
          <h2>Crear Líneas</h2>
          <label htmlFor="orden">Order Number:</label>
          <input
            type="text"
            id="orden"
            value={orden}
            onChange={(e) => setOrden(e.target.value)}
            required
          />
          <label htmlFor="startPrice">Start Price:</label>
          <input 
            type="number" 
            id="startPrice" 
            value={startPrice} 
            onChange={(e) => setStartPrice(parseFloat(e.target.value))} 
            required 
          />
          <label htmlFor="endPrice">End Price:</label>
          <input 
            type="number" 
            id="endPrice" 
            value={endPrice} 
            onChange={(e) => setEndPrice(parseFloat(e.target.value))} 
            required 
          />
          <label htmlFor="lineNameTemplate">Line Name:</label>
          <input
            type="text"
            id="lineNameTemplate"
            value={lineNameTemplate}
            onChange={(e) => setLineNameTemplate(e.target.value)}
            required
          />
          <label htmlFor="lineItemType">Line Type:</label>
          <input
            type="text"
            id="lineItemType"
            value={lineItemType}
            onChange={(e) => setLineItemType(e.target.value.toUpperCase())}
            required
          />
          <label htmlFor="priority">Priority value:</label>
          <input
            type="number"
            id="priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value)}
            required
          />
          <label htmlFor="expectedCreative">Expected Creative Size:</label>
          <select
            id="expectedCreative"
            value={expectedCreative}
            onChange={(e) => setExpectedCreative(e.target.value)}
            required
          >
            <option value="">Selecciona una opción</option>
            <option value="728x90">728x90</option>
            <option value="1x1">1x1</option>
          </select>
          <label htmlFor="deliverySettings">Delivery Settings:</label>
          <select
            id="deliverySettings"
            value={deliverySettings}
            onChange={(e) => setDeliverySettings(e.target.value)}
            required
          >
            <option value="IMMEDIATELY">IMMEDIATELY</option>
            <option value="CUSTOM">Custom Date and Time</option>
          </select>
          {deliverySettings === 'CUSTOM' && (
            <>
              <input
                type="text"
                id="customDate"
                placeholder="DD/MM/YYYY"
                value={customDate}
                onChange={(e) => setCustomDate(e.target.value)}
                required
              />
              <input
                type="time"
                id="customTime"
                value={customTime}
                onChange={(e) => setCustomTime(e.target.value)}
                required
              />
            </>
          )}
          <label htmlFor="endSettings">End Settings:</label>
          <select
            id="endSettings"
            value={endSettings}
            onChange={(e) => setEndSettings(e.target.value)}
            required
          >
            <option value="UNLIMITED">UNLIMITED</option>
            <option value="CUSTOM">Custom End Date and Time</option>
          </select>
          {endSettings === 'CUSTOM' && (
            <>
              <input
                type="text"
                id="endDate"
                placeholder="DD/MM/YYYY"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                required
              />
              <input
                type="time"
                id="endTime"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                required
              />
            </>
          )}
          <label htmlFor="goalUnits">Goal (% of total impressions):</label>
          <input
            type="number"
            id="goalUnits"
            value={goalUnits}
            onChange={(e) => setGoalUnits(parseInt(e.target.value))}
            required
          />
          <label htmlFor="creativeRotationType">Rotate creatives:</label>
          <select
            id="creativeRotationType"
            value={creativeRotationType}
            onChange={(e) => setCreativeRotationType(e.target.value)}
            required
          >
            <option value="EVEN">Evenly</option>
            <option value="OPTIMIZED">Optimised</option>
            <option value="WEIGHTED">Weighted</option>
            <option value="SEQUENTIAL">Sequential</option>
          </select>
          <label htmlFor="roadblockingType">Display creatives:</label>
          <select
            id="roadblockingType"
            value={roadblockingType}
            onChange={(e) => setRoadblockingType(e.target.value)}
            required
          >
            <option value="ONLY_ONE">Only one</option>
            <option value="ONE_OR_MORE">One or more</option>
            <option value="AS_MANY_AS_POSSIBLE">As many as possible</option>
            <option value="ALL_ROADBLOCK">All</option>
          </select>
          <label htmlFor="inventoryInclude">Inventory Include:</label>
          <select
            id="inventoryInclude"
            value={inventoryInclude}
            onChange={(e) => setInventoryInclude([...e.target.selectedOptions].map(option => option.value))}
            multiple
            required
          >
            <option value="LV">LV</option>
            <option value="MD">MD</option>
            <option value="RAC1">RAC1</option>
          </select>
          <label htmlFor="inventoryExclude">Inventory Exclude:</label>
          <select
            id="inventoryExclude"
            value={inventoryExclude}
            onChange={(e) => setInventoryExclude([...e.target.selectedOptions].map(option => option.value))}
            multiple
            required
          >
            <option value="comer">Comer</option>
            <option value="historiayvida">Historia y Vida</option>
            <option value="magazine">Magazine</option>
            <option value="motor">Motor</option>
          </select>
          <label htmlFor="customTargeting">Custom Targeting (Cat):</label>
          <select
            id="customTargeting"
            value={customTargeting}
            onChange={(e) => setCustomTargeting([...e.target.selectedOptions].map(option => option.value))}
            multiple
            required
          >
            <option value="208473659844">Story Viral</option>
            <option value="174650883684">Story</option>
            <option value="189633282084">Live</option>
          </select>
          <label htmlFor="placement">Placement (Mega1):</label>
          <select
            id="placement"
            value={placement}
            onChange={(e) => setPlacement(e.target.value)}
            required
          >
            <option value="">Selecciona una opción</option>
            <option value="84198161484">Mega1</option>
          </select>
          <label htmlFor="diseño">Diseño:</label>
          <select
            id="diseño"
            value={diseño}
            onChange={(e) => setDiseño(e.target.value)}
            required
          >
            <option value="">Selecciona una opción</option>
            <option value="104139488484">XS</option>
            <option value="104139488004">SM</option>
            <option value="104139487764">MD</option>
          </select>
          <label htmlFor="articleCount">Article Count:</label>
          <select
            id="articleCount"
            value={articleCount}
            onChange={(e) => setArticleCount(e.target.value)}
            required
          >
            <option value="">Selecciona una opción</option>
            <option value="448206030155">1</option>
          </select>
          <label htmlFor="hbDeal">HB Deal (IS any of):</label>
          <select
            id="hbDeal"
            value={hbDeal}
            onChange={(e) => setHbDeal([...e.target.selectedOptions].map(option => option.value))}
            multiple
            required
          >
            <option value="448131355960">ramkt</option>
            <option value="448290974564">appnexus</option>
            <option value="448995603719">6679bf7986</option>
            <option value="448148134169">1jtx0Zr90r</option>
            <option value="448995234300">86a6fb0e60</option>
            <option value="448148134169">1jtx0Zr90r</option>
          </select>
          <label htmlFor="hbDealNone">HB Deal (IS none of):</label>
          <select
            id="hbDealNone"
            value={hbDealNone}
            onChange={(e) => setHbDealNone([...e.target.selectedOptions].map(option => option.value))}
            multiple
            required
          >
            <option value="448131355960">ramkt</option>
            <option value="448290974564">appnexus</option>
            <option value="448995603719">6679bf7986</option>
            <option value="448148134169">1jtx0Zr90r</option>
            <option value="448995234300">86a6fb0e60</option>
            <option value="448148134169">1jtx0Zr90r</option>
          </select>
          <button type="submit" disabled={isProcessing}>Crear Línea</button>
          <button type="button" onClick={() => setMode('')}>Volver al inicio</button>
        </form>
      )}

      {mode === 'update' && (
        <form onSubmit={handleUpdateSubmit}>
          <h2>Actualizar Líneas</h2>
          <label htmlFor="orden">Order Number:</label>
          <input
            type="text"
            id="orden"
            value={orden}
            onChange={(e) => setOrden(e.target.value)}
          />
          <label htmlFor="hbDeal">HB Deal (IS any of):</label>
          <select
            id="hbDeal"
            value={hbDeal}
            onChange={(e) => setHbDeal([...e.target.selectedOptions].map(option => option.value))}
            multiple
          >
            <option value="448131355960">ramkt</option>
            <option value="448290974564">appnexus</option>
            <option value="448995603719">6679bf7986</option>
            <option value="448148134169">1jtx0Zr90r</option>
            <option value="448995234300">86a6fb0e60</option>
            <option value="448148134169">1jtx0Zr90r</option>
          </select>
          <label htmlFor="hbDealNone">HB Deal (IS none of):</label>
          <select
            id="hbDealNone"
            value={hbDealNone}
            onChange={(e) => setHbDealNone([...e.target.selectedOptions].map(option => option.value))}
            multiple
          >
            <option value="448131355960">ramkt</option>
            <option value="448290974564">appnexus</option>
            <option value="448995603719">6679bf7986</option>
            <option value="448148134169">1jtx0Zr90r</option>
            <option value="448995234300">86a6fb0e60</option>
            <option value="448148134169">1jtx0Zr90r</option>
          </select>
          <label htmlFor="hbDealRemove">Remove HB Deal (IS any of):</label>
          <select
            id="hbDealRemove"
            value={hbDealRemove}
            onChange={(e) => setHbDealRemove([...e.target.selectedOptions].map(option => option.value))}
            multiple
          >
            <option value="448131355960">ramkt</option>
            <option value="448290974564">appnexus</option>
            <option value="448995603719">6679bf7986</option>
            <option value="448148134169">1jtx0Zr90r</option>
            <option value="448995234300">86a6fb0e60</option>
            <option value="448148134169">1jtx0Zr90r</option>
          </select>
          <label htmlFor="hbDealNoneRemove">Remove HB Deal (IS none of):</label>
          <select
            id="hbDealNoneRemove"
            value={hbDealNoneRemove}
            onChange={(e) => setHbDealNoneRemove([...e.target.selectedOptions].map(option => option.value))}
            multiple
          >
            <option value="448131355960">ramkt</option>
            <option value="448290974564">appnexus</option>
            <option value="448995603719">6679bf7986</option>
            <option value="448148134169">1jtx0Zr90r</option>
            <option value="448995234300">86a6fb0e60</option>
            <option value="448148134169">1jtx0Zr90r</option>
          </select>
          <label htmlFor="lineItemType">Line Type:</label>
          <input
            type="text"
            id="lineItemType"
            value={lineItemType}
            onChange={(e) => setLineItemType(e.target.value.toUpperCase())}
          />
          <label htmlFor="priority">Priority value:</label>
          <input
            type="number"
            id="priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value)}
          />
          <label htmlFor="expectedCreative">Expected Creative Sizes:</label>
          <select
            id="expectedCreative"
            value={expectedCreative}
            onChange={(e) => setExpectedCreative([...e.target.selectedOptions].map(option => option.value))}
            multiple
          >
            <option value="728x90">728x90</option>
            <option value="1x1">1x1</option>
            <option value="300x250">300x250</option>
          </select>
          <label htmlFor="minCPM">CPM Mínimo (€):</label>
            <input
              type="number"
              id="minCPM"
              value={minCPM}
              onChange={(e) => setMinCPM(parseFloat(e.target.value))}
          />
          <label htmlFor="startTimeOption">Start Time:</label>
          <select
            id="startTimeOption"
            value={startTimeOption}
            onChange={(e) => setStartTimeOption(e.target.value)}
          >
            <option value="IMMEDIATELY">Immediately</option>
            <option value="ONE_HOUR">One Hour from Now</option>
            <option value="CUSTOM">Custom Date</option>
          </select>
          {startTimeOption === "CUSTOM" && (
            <>
              <input
                type="text"
                id="startDate"
                placeholder="DD/MM/YYYY"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                required
              />
              <input
                type="time"
                id="startTime"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                required
              />
            </>
          )}

          <label htmlFor="endTimeOption">End Time:</label>
          <select
            id="endTimeOption"
            value={endTimeOption}
            onChange={(e) => setEndTimeOption(e.target.value)}
          >
            <option value="UNLIMITED">Unlimited</option>
            <option value="CUSTOM">Custom End Date</option>
          </select>
          {endTimeOption === "CUSTOM" && (
            <>
              <input
                type="text"
                id="endDate"
                placeholder="DD/MM/YYYY"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                required
              />
              <input
                type="time"
                id="endTime"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                required
              />
            </>
          )}
          <button type="submit" disabled={isProcessing}>Actualizar Línea</button>
          <button type="button" onClick={() => setMode('')}>Volver al inicio</button>
        </form>
      )}

      {isProcessing && <p>{mode === 'create' ? 'Creando' : 'Actualizando'} líneas...</p>}
      {resultado && <p>{resultado}</p>}
    </div>
  );
}

export default App;
