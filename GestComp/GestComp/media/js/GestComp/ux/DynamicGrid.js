   	Ext.define('GestComp.ux.DynamicGrid',{
    		extend:'Ext.grid.Panel',
    		alias:'widget.dynamicgrid',
    		initComponent: function(){
    			
    			this.metaStore = Ext.create('Ext.data.Store',{
    					autoLoad:false,
    					fields:['columns','data','metaData','fields'],
    					proxy: {
        					type: 'ajax',
        					url : 'evaluations/resultats_eval',
        					reader: {
            					type: 'json',
            					root: 'toutdata'
        					},
        				//extraParams:{id:199}
    					},
    			});
    			/*
    			 * premiere option : on cré un model dynamique + 1 store
    			 * bien si peu de grilles (genre 1)
    			 */
    			this.modelFactory=function (name, fields) {
    				return Ext.define(name, {
        				extend: 'Ext.data.Model',
        				fields: fields
    				});    				
				};
				this.storeFactory=function(name,model,data){
   					 return Ext.create('Ext.data.Store',
    					{
    					autoLoad:false,
    					model:model,
    					data:data,
    					proxy:{
    						type:'ajax',
    						url:'bidon',
    						reader: {
            					type: 'json',            	
        					},
    					}
    				})
				};
				/*
				 * deuxième option, on ne passe pas par la case model, 
				 * on utilise directement les fields
				 * bien en cas de multiple grids
				 */
				this.storeFactory_bis=function(name,fields,data){
   					 return Ext.create('Ext.data.Store',
    					{
    					autoLoad:false,
    					fields:fields,
    					data:data,
    					proxy:{
    						type:'ajax',
    						url:'bidon',
    						reader: {
            					type: 'json',            	
        					},
    					}
    				})
				};
				// création d'un store bidon au départ
				// méthode 1:
				//var model=this.modelFactory('modelfx',[{name:'id'}])
				//this.store=this.storeFactory('storefx',model,[{}])
				//méthode 2:
				this.store=this.storeFactory_bis('storefx',[],[{}]);
				
				//création de colonnes bidons, 
				// si on veut une grid lockable, il faut créer une colonne lockée
				if (this.gridlockable) this.columns=[{text:'',dataIndex:'id',locked:true}];
				else this.columns=[];
				
				this.columnLines= true;
				this.callParent();
				
				this.metaStore.on('beforeload',function(st,op,opt){
					//console.log('before',op.id, this.eval_charge_id?"chareg":"pas charge")
					//this.eval_charge_id=op.id					
					}
					,this);
					
				this.metaStore.on('load',function(st,records,success,operation,options) {
					this.eval_id=this.eval_charge_id
					this.eval_charge_id=null
					//methode 1
					//var model=this.modelFactory('modelfx'+this.eval_id,records[0].get('fields'))
    				//var store=this.storeFactory('storefx',model,records[0].get('data'))
					//methode 2
    				var store=this.storeFactory_bis('storefx',records[0].get('fields'),records[0].get('data'))
    				
    				if (typeof(this.modifStore)!="undefined") store=this.modifStore(store,records[0].get('metaData'))
    				// définition des colonnes, surcharge possible d'une colonne avec modifColumn
					columns=this.getColumns(records[0])
					
					//reconfiguration
					this.reconfigure(store,columns)
				},this)
    		},
    		getColumns:function(record) { 
    			//console.log('cols par def')
				columns = [{
        			text: 'ID',
        			sortable: true,
        			dataIndex: 'eleve_id',
        			hidden:true,
        			locked:false,
        		}];
        		cols=record.get('columns')
        		for (var i = 0; i < cols.length; i++) {
        			// gestion des templates
        			tpl=cols[i].tpl
        			if (tpl && cols[i].xtype=='templatecolumn' && tpl.indexOf('Ext.XTemplate')!=-1) tpl=eval(tpl)
        			if (typeof(cols[i].renderer)!='undefined') {
        				eval("renderer="+cols[i].renderer)
        			}
        			else renderer=null 
        			
        			//construction de la config des colonnes
        			columns[i+1] = {
            				text: cols[i].header,
            				sortable: cols[i].sortable,
            				dataIndex: cols[i].dataIndex,
            				xtype: cols[i].xtype,
            				renderer:renderer,
            				tpl:tpl,
            				locked:cols[i].locked 
    				}
    				columns[i+1]=this.modifColumn(columns[i+1],cols[i],i)
        		}
    			
    		return columns
    		},
    		// modifie la colonne construite avant reconfigure
    		modifColumn:function(column,columnRecue,index) {return column},
    		reload:function(id) {this.metaStore.load(extraParams={id:id})}
 
    	});

 