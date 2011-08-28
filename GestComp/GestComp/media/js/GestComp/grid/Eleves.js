Ext.define('GestComp.grid.Eleves',{
	requires:['GestComp.stores.eleves', 'Ext.ux.grid.FiltersFeature'],
	//alias:'widget.grideleves',
	extend:'Ext.grid.Panel',
	title:'Grille élève(défaut)',
	
	initComponent: function(){
		Ext.apply(this, {
           store:GestComp.Eleves,
           features: [{
           	ftype:'grouping',
           	startCollapsed:true,
           	groupHeaderTpl:'Groupe: {name} ({rows.length} élève{[values.rows.length > 1 ? "s" : ""]})'
           },{
            ftype: 'filters',
			type: 'filters',
			encode: true,
			local: true,
			autoReload: false,
           }
           ],
		   columns:[
				{header:'id',dataIndex:'id',hidden:true},
				{header:'Nom',dataIndex:'nom',filterable:true,
				renderer:function(value,metaData,record,rowindex,colIndex,store,view) {
					metaData.tdAttr='data-qtip="'+'test'+value+'--" data-qtitle="TEST"';
					return value
					},
				},
				{header:'Prénom',dataIndex:'prenom',filterable:true,
				renderer:function(value,metaData,record,rowindex,colIndex,store,view) {
					//metaData.tdCls='essai'
					return value
					}
				},
				{header:'classe',dataIndex:'classe',filterable:true,width:40,
				},
				{header:'groupes',dataIndex:'groupes'},
				{header:'liste groupes',dataIndex:'groupesliste',filterable:true,
					
				}
			],
     	 });
		GestComp.grid.Eleves.superclass.initComponent.apply(this, arguments);
		this.on({afterlayout:{scope:this, single:true, fn:function() {
							this.store.load({params:{start:0}})
			}}
        });
        
        /* 
         * Exemple de qtip dynamique (sur une ligne)
         */
        this.getView().on('render', function(view) {
        	console.log("sel",view.itemSelector)
    		view.tip = Ext.create('Ext.tip.ToolTip', {
        // 		The overall target element.
        		target: view.el,
        // 		Each grid row causes its own seperate show and hide.
        		delegate: view.itemSelector,
        		/*
        		 * question: avec delegate:".essai", sur une colonne,
        		 * comment récupérer la ligne?
        		 * ie comment faire avec le tip.triggerElement? 
        		 */
        		
        // 		Moving within the row should not hide the tip.
        		trackMouse: true,
        		// ne disparait que lorsque qu'on sort de la cible
        		dismissDelay:0,
        // 		Render immediately so that tip.body can be referenced prior to the first show.
        		renderTo: Ext.getBody(),
        		/*
        		 * premiere méthode: avec tpl et les données en json : renderer:'data'
        		 * (pas de reader definissable(?) donc envois direct des données JSON coté serveur {nom:'truc',prenom:'bidule'}
        		 * ou bien passer par la méthode "success" et décoder
        		 * 
        		 * deuxième méthode: retour dirct en html: renderer:'html' (defaut)
        		 * côté serveur sous django : 
        		 * 	resp=HttpResponse()
        		 *  resp.write('<p>truc</p>')
        		 *  resp.write('<i>bidue</i>')
        		 *  return resp
        		 */
        		tpl:'<p>nom:<p><tpl>{nom}</tpl>',
        		loader: {
        			url: '/utilisateurs/infos_eleve',
        			loadMask:true,
        			renderer: 'data',
        			params: {
            			userId: 1            		
        			},        			
    			},

    			listeners: {
            // Change content dynamically depending on which element triggered the show.
            		beforeshow: function updateTipBody(tip) {
            			console.log('trigger',tip.triggerElement)
            			record=view.getRecord(tip.triggerElement);
            			
            			this.getLoader().load({params:{id:record.data.id}})
            			
                		// ou : tip.update('Over company "' + view.getRecord(tip.triggerElement).get('groupes') + '"');
            		}
            		
        	}
    	});
});
        
        
	}
});