# Handover time series and comparison 

## Preprocessing  

`python3 create_dataset.py ./location_dataset ./location_dataset_out`

- Day  
- Timestamp  
- QoS Tester_QP Interactivity Progress_Cur. Interactivity Score [%]  
- 5G NR UE_Cell Environment_1. PCI  
- QoS Tester_QP Interactivity Progress_Cur. Num. Lost Packets  

`<input CSV path>`  
├── location_4  
│   ├── location_4_od_interactivity_egaming_it_tv_tti_0.csv  
│   ├── location_4_od_interactivity_egaming_it_tv_tti_1.csv  
│   └── location_4_od_interactivity_egaming_it_tv_tti_2.csv  
├── location_7  
│   ├── location_7_od_interactivity_egaming_ch_tv_tti_0.csv  
│   ├── location_7_od_interactivity_egaming_ch_tv_tti_1.csv  
│   └── location_7_od_interactivity_egaming_ch_tv_tti_2.csv  
├── location_9  
|   ├── location_9_od_interactivity_egaming_it_tv_tti_0.csv  
|   ├── location_9_od_interactivity_egaming_it_tv_tti_1.csv  
|   └── location_9_od_interactivity_egaming_it_tv_tti_2.csv  

`<output CSV path>`  
├── location_4  
│   ├── location_4_od_interactivity_egaming_it_tv_tti_0.csv  
│   ├── location_4_od_interactivity_egaming_it_tv_tti_1.csv  
│   └── location_4_od_interactivity_egaming_it_tv_tti_2.csv  
├── location_7  
│   ├── location_7_od_interactivity_egaming_ch_tv_tti_0.csv  
│   ├── location_7_od_interactivity_egaming_ch_tv_tti_1.csv  
│   └── location_7_od_interactivity_egaming_ch_tv_tti_2.csv  
├─ location_9  
|   ├── location_9_od_interactivity_egaming_it_tv_tti_0.csv  
|   ├── location_9_od_interactivity_egaming_it_tv_tti_1.csv  
|   └── location_9_od_interactivity_egaming_it_tv_tti_2.csv  

## Handover detection

python3 ./capture_handovers.py <input processed CSV path> <output aggregated CSVs path>  

<input processed CSV path>  
├── location_4  
│   ├── location_4_od_interactivity_egaming_it_tv_tti_0.csv  
│   ├── location_4_od_interactivity_egaming_it_tv_tti_1.csv  
│   └── location_4_od_interactivity_egaming_it_tv_tti_2.csv  
├── location_7  
│   ├── location_7_od_interactivity_egaming_ch_tv_tti_0.csv  
│   ├── location_7_od_interactivity_egaming_ch_tv_tti_1.csv  
│   └── location_7_od_interactivity_egaming_ch_tv_tti_2.csv  
├─ location_9  
|   ├── location_9_od_interactivity_egaming_it_tv_tti_0.csv  
|   ├── location_9_od_interactivity_egaming_it_tv_tti_1.csv  
|   └── location_9_od_interactivity_egaming_it_tv_tti_2.csv  

`<output aggregated CSVs path>`  
├── location_4_aggregated.csv  
├── location_4_aggregated.json  
├── location_9_aggregated.csv  
└── location_9_aggregated.json  
