Ext.define('GestComp.Prof.view.navigation.Evaluation',{
	requires:[
		'GestComp.Prof.store.Evaluations', 
		'Ext.ux.grid.FiltersFeature',
		
	],
	alias:'widget.navigation_evaluation',
	extend:'Ext.grid.Panel',	
	title:'Grille évaluation(défaut)',
	store:'Evaluations',
	initComponent: function(){
		var me=this
		
		var tp=new Ext.XTemplate('ff:{name}')
		this.features= [{
           	ftype:'grouping',
           	startCollapsed:true,
           	// is on cache la colonne, les fltres ne fonctionnent plus..., il va falloir la cacher après le rendu des filtres
           	//hideGroupedHeader:true,
           	groupHeaderTpl:'{header}: {renderedValue} ({rows.length} évaluation{[values.rows.length > 1 ? "s" : ""]})',           	
           }
           ,{
            ftype: 'filters',
			type: 'filters',
			encode: true,
			local: true,
			autoReload: false,
           }
           ];
        this.columns=[
			{header:'id',dataIndex:'id',hidden:true},
			{header:'créateur',dataIndex:'perso',
    	    	xtype:'booleancolumn', width:30,sortable:true,
    	    	trueText: 'Moi',
            	falseText: 'Collègue', 
				filterable:false,			  					
			},
			{header:'nom',dataIndex:'nom',filterable:true},
			{header:'modification', dataIndex:'date_modification',
        	 	xtype: 'datecolumn', format: 'd/m/Y', filterable:true,	
        	 },
        	 {header:'date',dataIndex:'date_evaluation',
        		xtype: 'datecolumn', format: 'd/m/Y',filterable:true
        	},
        	{header:'Créé par',dataIndex:'user',filterable:true}
        			     
        ]; 
        
        this.callParent() 
        
        
	}
});