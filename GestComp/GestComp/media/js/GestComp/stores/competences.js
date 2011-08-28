Ext.define('GestComp.stores.competences.CompetenceModel',{
	extend:'Ext.data.Model',
	fields:['id','nom','chemin','description'],
	proxy:{
		type:'ajax',
		url:'/competences/liste_competences',
		reader: {
            type: 'json',
            root: 'data'
        },
        extraParams: {
                action: 'liste'
            },
        
	},
	
});
GestComp.Competences = Ext.create('Ext.data.Store',{
	//autoLoad: true,
	model:'GestComp.stores.competences.CompetenceModel',
	
	listeners:{		
		'load':function(){GestComp.Message.fireEvent('message',this,'Liste Compétences','chargée')}
		}
	
});

Ext.define('GestComp.stores.competences.CompetenceTreeModel',{	
		extend:'Ext.data.Model',
		fields:['id','text','nom','description','user','tree',
			'competence_id', 'feuille','graphe','is_root','niveau','qtip','type_lien'
		],
		proxy:{
			type:'ajax',
			url:"/competences/retourbranche",
			reader: {
            	type: 'json',
            	root: 'data'
        	},
			extraParams: {lazy:'True',pos:'gauche'},
		},        
});

Ext.define('GestComp.stores.competences.CompetenceTree',{
	extend:'Ext.data.TreeStore',
	alias:'widget.tt',
	autoLoad:false,
	model:'GestComp.stores.competences.CompetenceTreeModel',
	sorters:[{property:'tree',direction:'DESC'},{property:'nom',direction:'DESC'}],
	constructor: function() {
		Ext.apply(this,{
			root: {	
				text: 'Menu',
				id: 'src',
				expanded: true
			},
		});
		this.callParent(arguments);
	}	
});

