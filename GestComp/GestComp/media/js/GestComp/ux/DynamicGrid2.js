Ext.require(['Ext.data.*', 'Ext.grid.*']);

Ext.define('dynamicModel', {
    extend: 'Ext.data.Model',
	fields: [ ]	// are defined in the JSON response metaData
});

Ext.define('GestComp.ux.DynamicGrid2',{
	extend:'Ext.grid.Panel',
	alias:'widget.dynamicgrid',
	//mixins: {lockable:'Ext.grid.Lockable'},
	initComponent: function(){
		//this.lockable=true;

		
		this.selType= 'cellmodel';
		this.stateful=false;
		this.store = Ext.create('Ext.data.Store', {
			storeId:'teststore',
			autoLoad: false,
			autoSync: true,			
			model: 'dynamicModel',			
			proxy: {
				type: 'ajax',
				api: {
					read: 'evaluations/resultats_eval',
					create :'evaluations/create_eval',
					update:'evaluations/modif_resultats',
					destroy:'evaluations/supprime_eval'
				},
				reader: {
					type: 'json', 
					//root: 'toutdata'
				},
				writer: {
					type:'json',
					writeAllFields:false,
					root:'data'
				}
			},
			listeners: {
				/*
				 	update: function(store,record,operation) {
				 		console.info('UPDATE',record.modified,operation)
				 	},
				 */
				/*
				 	datachanged: function(store){console.info('DATACHANGED')},
				 */
				/*
				 	beforesync:function(options) {
				 		console.info('BEFORESYNC',options,options.update[0].modified,options.update[0].dirty,this)
				 		// pour 1 record
				 		for (rec in options.update) {
				 			var donnees_modifie=false
				 			 
				 			for (var r in options.update[rec].modified) {
				 				donnees_modifie=donnees_modifie || (r.indexOf('donnees')!=-1)
				 			}
				 			console.info('update',options.update[rec].modified,donnees_modifie)
				 			
				 		}		 		
				 	},
				 */
				/*
		            write: function(store, operation){		            	
		            		console.log('wrtie',operation,operation.action,operation.isComplete(),operation.records[0])		          
		            }
		        */
		        }
		});
        //this.columns= [{text:'test',dataIndex:'col1',width:30},{text:'truc',dataIndex:'col2'}]
		
		this.columns={
				defaults: {
				locked:true,
				/*field: {
					xtype: 'textfield'
				}*/
			}
		};	
		var me=this
		
		this.callParent()
		
		this.store.on('load',function(store,records,success,op) {
			if (typeof(this.modifStore)!="undefined") store=this.modifStore(store,records[0].get('metaData'))
			var cols=this.getColumns(records[0].store.proxy.reader.columns)
			//console.log('EVAL',records[0].store.proxy.reader.eval)
			this.eval=records[0].store.proxy.reader.eval
			this.reconfigure(this.store,cols)
			
			//this.show()   
		},this)
		this.store.on('beforeload',function() {
			// nécessaire car il y a un overwrite des tpls avant la fin du load... curieux
			// bug levé dans la 4.0.5?
			for (var i=0;i<this.columns.length;i++) {
				this.columns[i].tpl='<tpl>rien</tpl>'
			}
			this.reconfigure(this.store,this.columns)
		},this)
		
	},

	modifColumns:function(columnRecue,index) {return columnRecue},
	getColumns:function(cols) {
		var columns=[];
		for (var i = 0; i < cols.length; i++) {			
			columns[i]=this.modifColumn(cols[i],i)
		}
		return columns
	},
	reload:function(id) {
			this.store.load(
					{	
						id:id				 					
					}
			)
	}
	
});