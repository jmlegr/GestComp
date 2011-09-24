Ext.define('GestComp.Prof.view.navigation.Eleve',{
	requires:['GestComp.Prof.store.Eleves', 'Ext.ux.grid.FiltersFeature'],
	alias:'widget.navigation_eleve',
	extend:'Ext.grid.Panel',
	title:'Grille élève(défaut)',
	store:'Eleves',
	initComponent: function(){
		this.features= [{
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
           ];
		var cellEditing = Ext.create('Ext.grid.plugin.CellEditing', {
	        clicksToEdit: 1
	    });
		this.plugins=[cellEditing];
		this.columns=[
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
			];
		this.callParent()    
        
	}
});