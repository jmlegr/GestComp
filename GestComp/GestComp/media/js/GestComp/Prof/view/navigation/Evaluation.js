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
		
		//var tp=new Ext.XTemplate('ff:{name}')
		//calcul de la date de la rentrée pour être large, fixée au 15 aout
		var today=new Date()
		var date_rentree=new Date(today.getMonth()>=8?today.getFullYear():today.getFullYear()-1,7,15)
		var zedate=new Date(2010,1,1)
		var filters={
	            ftype: 'filters',
				//type: 'filters',
				//encode: true, pour envoie du filtre en json
				local: true,
				//autoReload: false,
				menuFilterText:'Filtre',			
				//filterCls:'ux-filtered-columnTEST',
				filters:[{
		        	   type:'string',
		        	   dataIndex:'nom',
		        	   value:'i'
				},{
					type:'date',
					dataIndex:'date_evaluation',
					 afterText:'Après',
		             beforeText:'Avant',
					//value:{after:zedate} --> ne marche pas
				}]
	           }
		this.features= [{
           	ftype:'grouping',
           	startCollapsed:true,
           	// is on cache la colonne, les fltres ne fonctionnent plus..., il va falloir la cacher après le rendu des filtres
           	//hideGroupedHeader:true,
           	groupHeaderTpl:'{header}: {renderedValue} ({rows.length} évaluation{[values.rows.length > 1 ? "s" : ""]})',           	
           }
           ,filters
           ];
		// TODO: voir si on peut cacher le groupedHeader evec les nouvelles versions ExtJs
		// pour l'instant on rajoute l'attribut 'cachee' à la colonne qu'on veut cacher après render
        this.columns=[
			{header:'id',dataIndex:'id',hidden:true},
			{header:'créateur',dataIndex:'perso',
    	    	xtype:'booleancolumn', width:30,sortable:true, cachee:true,
    	    	trueText: 'Moi',
            	falseText: 'Collègue', 
				filterable:false,			  					
			},
			{header:'nom',dataIndex:'nom'
			
			},			
			{header:'modification', dataIndex:'date_modification',
        	 	xtype: 'datecolumn', format: 'd/m/Y',filterable:true,
        	 	
        	 	filter:{
	                type: 'date',
	                afterText:'Après',
	                beforeText:'Avant',
	    			onText : 'Le',
	            }
        	 },
        	 {header:'date',dataIndex:'date_evaluation',
        		xtype: 'datecolumn', format: 'd/m/Y',filterable:true,
        		filter:{
	                type: 'date',
	                afterText:'Après',
	                beforeText:'Avant',
	    			onText : 'Le',
	            }        		
        	},
        	{header:'Créé par',dataIndex:'user',filterable:true}
        			     
        ]; 
        
        this.callParent() 
        //console.log('this',this.filters.view.rendered)
        this.on('afterrender', function(){
        		/* curieusement, les filtres ne semblent pas exister tant qu'on ne les a pas créés
        		 * même s'ils sont dans la config et que le menu est là...
        		 * on recré volontairement un filtre sur la date et on l'active
        		 */
        		//Ext.util.Observable.capture(Ext.getCmp('navEvaluations'), console.info)
        		this.filters.addFilter({
					  type: 'date',
		                dataIndex:'date_modification',
		    			value:{after:zedate}
		                //value:{after:date_rentree}
				})
        		this.filters.getFilter('date_modification').setActive(true);
        		
        		/*
        		 * on cache les colonnes avec l'attribut "cachee"
        		 */
        		Ext.each(this.headerCt.gridDataColumns,function(c) {
        				if (c.cachee) c.hide();
        		});
        },this,{single:true})
        
        
        
	}
});