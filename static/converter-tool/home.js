(function () {
    feather.replace()
})()


$(document).on("scroll", function(){
    if ($(document).scrollTop() > 60){
      if (document.getElementById('stuckNav') == null){
        var newNav = $('.nav-wrapper').clone(true);
        newNav.attr('id', 'stuckNav');
        $('.nav-wrapper').append(newNav);

      }
      

    }
    else
    {
      $('#stuckNav').remove();
    }
});


var app = new Vue({
delimiters: ['[[', ']]'],
el: '#app',
data:{
  file_name: '',
  progress: 'Converting',
  wbBlob: [],
  pptx_list: [],
  excel_name: [],
  pptx_name:[],
  response: {},
  response_two: [],
  error_msg: 'Not Demo Excel - Please Reupload',

},
  
mounted:function(){

},
methods:{
    dragover(event) {
      event.preventDefault();
      if (!event.currentTarget.classList.contains('drag-in')) {
        event.currentTarget.classList.add('drag-in');
      }
    },
    dragleave(event) {
      event.currentTarget.classList.remove('drag-in');
    },
    get_file(){          
      document.getElementById('file').click()      
    },
    drop(event) {
      event.preventDefault();
      this.$refs.file.files = event.dataTransfer.files;
      this.upload()
      event.currentTarget.classList.remove('drag-in');
    },
    getCookie (name) {
          var value = '; ' + document.cookie
          var parts = value.split('; ' + name + '=')
          if (parts.length === 2) return parts.pop().split(';').shift()
    },
    upload(){
        var self = this;

        

        const formData = new FormData();               
        let file_info = document.getElementById('file');
        let file = file_info.files[0];
        this.file_name = file.name
        var extension = file.name.substring(file.name.lastIndexOf(".") + 1)
        

        if( extension == 'xlsx'){
            document.getElementById("upload").classList.add("hide")
            document.getElementById("uploading").classList.remove("hide")
            formData.append(`host_excel`, file);     
            
            axios.post(``, formData, {
              headers: {'Content-Type': 'multipart/form-data'},
            
            }).then((response)=>{
              console.log(response)
      
              if (response.data['product_brand'] == null){
                document.getElementById("uploading").classList.add("hide")
                document.getElementById("uploaded-error").classList.remove("hide")

              } else {

                this.response = response.data
                this.progress = 'Converting Excel...'
                self.export_excel()       
              }

           
            }).catch(error => {
                console.log('error', error);
                this.error_msg = 'Please cut down demo file size to reduce processing time...'
                document.getElementById("uploading").classList.add("hide")
                document.getElementById("uploaded-error").classList.remove("hide")

            })


        } else {
          alert('Please Upload Demo Excel')
        }
        
    },
    sheet_from_array_of_arrays(data) {
        const ws = {};
        const range = {s: {c:10000000, r:10000000}, e: {c:0, r:0 }};
        for(let R = 0; R !== data.length; ++R) {
        for(let C = 0; C !== data[R].length; ++C) {
        if(range.s.r > R) range.s.r = R;
        if(range.s.c > C) range.s.c = C;
        if(range.e.r < R) range.e.r = R;
        if(range.e.c < C) range.e.c = C;

        const cell = {v: data[R][C], s: {
          font: { name: "Calibri", sz: 11, color: { auto: 1 } },
          border: {
          color: { auto: 1 }
          },
          alignment: {
          wrapText: 0,
          horizontal: "center",
          vertical: "center",
          indent: 0
          }
        }};
        if(cell.v == null) continue;
        const cell_ref = XLSX.utils.encode_cell({c:C,r:R});
        if(typeof cell.v === 'number') cell.t = 'n';
        else if(typeof cell.v === 'boolean') cell.t = 'b';
        else if(cell.v instanceof Date) {
        cell.t = 'n'; cell.z = XLSX.SSF._table[14];
        cell.v = this.dateNum(cell.v);
        }
        else cell.t = 's';
        ws[cell_ref] = cell;
        }
        }
        /* TEST: proper range */
        if(range.s.c < 10000000) ws['!ref'] = XLSX.utils.encode_range(range);
        return ws;
    },

    sheet2blob(sheet, sheetName,sheet2, sheetName2) {
      sheetName = sheetName || 'sheet1';
      sheetName2 = sheetName2 || 'sheet2';
      const workbook = {
      SheetNames: [sheetName, sheetName2],
      Sheets: {}
      };
      workbook.Sheets[sheetName] = sheet
      workbook.Sheets[sheetName2] = sheet2
      const wopts = {
      bookType: 'xlsx', 
      bookSST: false, 
      type: 'binary'
      };
     
      const wbout = XLSX.write(workbook, wopts,);
      const blob = new Blob([s2ab(wbout)], {type: "application/octet-stream"});
      function s2ab(s) {
      const buf = new ArrayBuffer(s.length);
      const view = new Uint8Array(buf);
      for (let i=0; i!==s.length; ++i) view[i] = s.charCodeAt(i) & 0xFF;
      return buf;
      }
      return blob;
    },

    export_excel(){   
      for (year of this.response.year_list){
        var title = this.response['product_brand'] + '渠道' + year + '年采购情况'
        var index = 1
        var index_list = []

        let aoa = [[title]]
        index = index + 2 
        index_list.push(index)
        aoa.push([])
        aoa.push.apply(aoa, this.response[year].total)
        index = index + this.response[year].total.length + 2
        index_list.push(index)
        aoa.push([])
        aoa.push(['采购数量'])
        aoa.push.apply(aoa, this.response[year].by_client_quantity)
        index = index + this.response[year].by_client_quantity.length + 2
        index_list.push(index)
        aoa.push([])
        aoa.push(['采购金额'])
        aoa.push.apply(aoa, this.response[year].by_client_payment)
        
        var sheet = this.sheet_from_array_of_arrays(aoa);
        

        const mergeTitle = [
          {
            s: {r: 0, c: 0},
            e: {r: 1, c: 13}
          },
          {
            s: {r: index_list[1]-2, c: 0},
            e: {r: index_list[1]-2, c: 13}
          },
          {
            s: {r: index_list[2]-2, c: 0},
            e: {r: index_list[2]-2, c: 13}
          },
        ]
        sheet['!merges'] = mergeTitle.concat();

        var filterRef = 'A' + index_list[1] + ':' + 'N' + index_list[1]                


 
        const sheetCols = [
          { wch: 20} , 
          { wch: 12} , 
          { wch: 12} , 
          { wch: 12} , 
          { wch: 12} , 
          { wch: 12} , 
          { wch: 12} , 
          { wch: 12} , 
          { wch: 12} , 
          { wch: 12} , 
          { wch: 12} , 
          { wch: 12} , 
          { wch: 12} , 
          { wch: 12} , 

        ];   

        sheet['!cols'] = sheetCols;
        for (i of ['A','B','C','D','E','F','G','H','I','J','K','L','M','N']){
          for (j of index_list){
            color_cell = i+j
            sheet[color_cell].s = {
              font: {
                name: 'Calibri',
                sz: 11,
                color: {rgb: "ffffff"},
                bold: true,
                italic: false,
                underline: false,
                // height: 20
              },
              alignment: {
                horizontal: "center",
                vertical: "center"
              },
              fill: {
                fgColor: {rgb: "16365C"},
              },
            };
          }
        }

        for (i of ['A1','A'+(index_list[1]-1),'A'+(index_list[2]-1)]){
          sheet[i].s = {
              font: {
                name: 'Calibri',
                sz: 11,
                color: {rgb: "000000"},
                bold: true,
                italic: false,
                underline: false,
                // height: 20
              },
              border: {
              color: { auto: 1 }
              },
              alignment: {
                horizontal: "center",
                vertical: "center"
              },
              fill: {
                fgColor: {rgb: "ffffff"},
              },
            };
        }

        for (i of ['B','C','D','E','F','G','H','I','J','K','L','M','N']){
          color_cell = i+'5'
          sheet[color_cell].s = {
            font: { name: "Calibri", sz: 11, color: { auto: 1 } },
            border: {
            color: { auto: 1 }
            },
            alignment: {
            wrapText: 0,
            horizontal: "center",
            vertical: "center",
            indent: 0
            },
            numFmt:  '_("$"* #,##0_);_("$"* (#,##0);_("$"* "-"??_);_(@_)'                 
          };
        }
   
        for (i of ['B','C','D','E','F','G','H','I','J','K','L','M','N']){
          var j = index_list[2] + 1
          var end = index_list[2] + this.response[year].by_client_payment.length
          

          while (j < end) {
            color_cell = i+j
            sheet[color_cell].s = {
              font: { name: "Calibri", sz: 11, color: { auto: 1 } },
              border: {
              color: { auto: 1 }
              },
              alignment: {
              wrapText: 0,
              horizontal: "center",
              vertical: "center",
              indent: 0
              },
              numFmt:  '_("$"* #,##0_);_("$"* (#,##0);_("$"* "-"??_);_(@_)'                 
            };

            j = j + 1
          } 
        }

        

        var title = this.response['product_brand'] + '单品'+ year +'年采购情况'
        var index = 1
        var index_list = []

        let aoa2 = [[title]]
        index = index + 2 
        index_list.push(index)
        aoa2.push([])
        for (i of this.response[year].total){
          var total_row = []
          total_row.push(i[0])
          total_row.push(null)
          total_row.push(null)
          total_row.push.apply(total_row,i.slice(1,))
          aoa2.push(total_row)
        }

        index = index + this.response[year].total.length + 2
        index_list.push(index)
        aoa2.push([])
        aoa2.push(['单品数量'])
        aoa2.push.apply(aoa2, this.response[year].by_product_quantity)
        index = index + this.response[year].by_product_quantity.length + 2
        index_list.push(index)
        aoa2.push([])
        aoa2.push(['单品金额'])
        aoa2.push.apply(aoa2, this.response[year].by_product_payment)
        
        var sheet2 = this.sheet_from_array_of_arrays(aoa2);

        const mergeTitle2 = [
          {
            s: {r: 0, c: 0},
            e: {r: 1, c: 15}
          },
          {
            s: {r: 2, c: 0},
            e: {r: 2, c: 2}
          },
          {
            s: {r: 3, c: 0},
            e: {r: 3, c: 2}
          },
          {
            s: {r: 4, c: 0},
            e: {r: 4, c: 2}
          },
          {
            s: {r: index_list[1]-2, c: 0},
            e: {r: index_list[1]-2, c: 15}
          },
          {
            s: {r: index_list[2]-2, c: 0},
            e: {r: index_list[2]-2, c: 15}
          },
        ]
        sheet2['!merges'] = mergeTitle2.concat();
        sheet2["!margins"] = { left: 1.0, right: 1.0, top: 1.0, bottom: 1.0, header: 0.5, footer: 0.5 }      
          
        const sheetCols2 = [
          { wch: 5} , 
          { wch: 5} , 
          { wch: 50} , 
          { wch: 12} , 
          { wch: 12} , 
          { wch: 12} , 
          { wch: 12} , 
          { wch: 12} , 
          { wch: 12} , 
          { wch: 12} , 
          { wch: 12} , 
          { wch: 12} , 
          { wch: 12} , 
          { wch: 12} , 
          { wch: 12} , 
          { wch: 12} , 
        ];   
        sheet2['!cols'] = sheetCols2;
        for (i of ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P']){
          for (j of index_list){
            if ((i =='B' || i =='C') && j == 3){
              continue
            } else {
              color_cell = i+j
              sheet2[color_cell].s = {
                font: {
                  name: 'Calibri',
                  sz: 11,
                  color: {rgb: "ffffff"},
                  bold: true,
                  italic: false,
                  underline: false,
                  // height: 20
                },
                alignment: {
                  horizontal: "center",
                  vertical: "center"
                },
                fill: {
                  fgColor: {rgb: "16365C"},
                },
              };

            }
            

            
          }
        }

        for (i of ['A1','A'+(index_list[1]-1),'A'+(index_list[2]-1)]){
          sheet2[i].s = {
              font: {
                name: 'Calibri',
                sz: 11,
                color: {rgb: "000000"},
                bold: true,
                italic: false,
                underline: false,
                // height: 20
              },
              border: {
              color: { auto: 1 }
              },
              alignment: {
                horizontal: "center",
                vertical: "center"
              },
              fill: {
                fgColor: {rgb: "ffffff"},
              },
            };
        }

        for (i of ['D','E','F','G','H','I','J','K','L','M','N','O','P']){
          color_cell = i+'5'
          sheet2[color_cell].s = {
            font: { name: "Calibri", sz: 11, color: { auto: 1 } },
            border: {
            color: { auto: 1 }
            },
            alignment: {
            wrapText: 0,
            horizontal: "center",
            vertical: "center",
            indent: 0
            },
            numFmt:  '_("$"* #,##0_);_("$"* (#,##0);_("$"* "-"??_);_(@_)'                 
          };
        }

        for (i of ['D','E','F','G','H','I','J','K','L','M','N','O','P']){
          var j = index_list[2] + 1
          var end = index_list[2] + this.response[year].by_product_payment.length
          

          while (j < end) {
            color_cell = i+j
            sheet2[color_cell].s = {
              font: { name: "Calibri", sz: 11, color: { auto: 1 } },
              border: {
              color: { auto: 1 }
              },
              alignment: {
              wrapText: 0,
              horizontal: "center",
              vertical: "center",
              indent: 0
              },
              numFmt:  '_("$"* #,##0_);_("$"* (#,##0);_("$"* "-"??_);_(@_)'                 
            };

            j = j + 1
          } 
        }
        this.wbBlob.push(this.sheet2blob(sheet, '渠道分析',sheet2, '单品分析'))
        var today = moment().format('YYMMDD');
        this.excel_name.push(this.response['product_brand'] + ' ' + year +'年销售明细帐分析v'+today+'.xlsx')
        // this.ppt_name.push(this.response['product_brand'] + ' ' + year +'年销售明细帐分析v'+today+'.pptx') 
        

        if (this.excel_name.length == this.response.year_list.length){
            this.progress = 'Converting PPT...'
            // document.getElementById("uploading").classList.add("hide")
            // document.getElementById("uploaded").classList.remove("hide")
            this.export_ppt()
        }

      }
            

    },
    
    download_excel(){
        var self = this
        this.wbBlob.forEach(function (value, i) {
            window.saveAs(value, self.excel_name[i])
        });
        
    },
    


    



    export_ppt(){
      this.response.year_list.forEach((year,idx)=>{
        var self = this
        let pptx = new PptxGenJS();
  
        pptx.layout = "LAYOUT_WIDE";

        var today_date = moment().format('YYYY/MM/DD');
  
        // 1:
        pptx.defineSlideMaster({
            title: "TITLE_SLIDE",
            background: { fill: "FFFFFF" },
            objects: [
              { image: { x: 11.3, y: 0.5, w: 1.2, h: 0.547, path: '/static/converter-tool/pic/logo2.png' } },
            ],
          });
        pptx.defineSlideMaster({
          title: "TITLE_SLIDE",
          background: { fill: "FFFFFF" },
          objects: [
            { image: { x: 11.3, y: 0.5, w: 1.2, h: 0.547, path: '/static/converter-tool/pic/logo2.png' } },
          ],
        });
  
        // 2:
        pptx.defineSlideMaster({
          title: "MASTER_SLIDE",
          background: { fill: "ffffff" },
          slideNumber: { x: 1.0, y: 7.15, color: "FFFFFF" },
          margin: [0.5, 0.25, 1.25, 0.25],
          objects: [
            { rect: { x: 0.3, y: 0.6, w: 2, h: 0.4, fill: { color: "A5A5A5" } } },
            { rect: { x: 0.5, y: 0.6, w: 2.5, h: 0.4, fill: { color: "333f50" } } },
            { rect: { x: 0.0, y: 7.1, w: "100%", h: 0.4, fill: { color: "000000" } } },
            {
              text: {
                text: "Health More Pty Ltd 内部使用 - " + today_date,
                options: { x: 0, y: 7.1, w: "100%", h: 0.4, align: "center", valign: "middle", color: "FFFFFF", fontFace: "Calibri", fontSize: 12 },
              },
            },
            { image: { x: 11.3, y: 0.5, w: 1.2, h: 0.547, path: '/static/converter-tool/pic/logo2.png' } },
          ],
        });

        this.genSlide01(pptx, year);
	      this.genSlide02(pptx, year);
	      this.genSlide03(pptx, year);
        this.genSlideMiddle(pptx, year);
        
        for (client of this.response[year].pptx_list){
          this.genClientSlide(pptx, year, client);
        }
        this.genSlideEnd(pptx, year);

        

  
  
  
      
        

        var today = moment().format('YYMMDD');

       
        var name = this.response['product_brand'] + ' ' + year +'年销售明细帐分析v'+today+'.pptx'
  
      
        this.pptx_list.push(pptx)
        this.pptx_name.push(name)
        if (this.pptx_name.length == this.response.year_list.length){
          document.getElementById("uploading").classList.add("hide")
          document.getElementById("uploaded").classList.remove("hide")
      }
      
        // pptx.writeFile({fileName:name});
        
      })    
    },

    download_ppt(){
      var self = this
      this.pptx_list.forEach((pptx,idx) => {
        pptx.writeFile({fileName: self.pptx_name[idx]})
      })

    },

    genSlide01(pptx, year) {
      let slide = pptx.addSlide({ masterName: "TITLE_SLIDE" });
  
      slide.addShape(pptx.shapes.RIGHT_TRIANGLE, {
        x: -3,
        y: 2.8,
        w: 8.2,
        h: 8.2,
        rotate: 135,
        line: { color: '333f50', width: 1.5 },
      });
      slide.addShape(pptx.shapes.RIGHT_TRIANGLE, {
        x: 0,
        y: 1.5,
        w: 5.5,
        h: 5.5,
        fill: { color: 'A6A6A6' },
      });
      slide.addShape(pptx.shapes.RIGHT_TRIANGLE, {
        x: 4,
        y: 2.2,
        w: 10.6,
        h: 10.6,
        rotate: 135,
        fill: { color: '333f50' },
      });

      slide.addShape(pptx.shapes.LINE, {
        x: 7.2,
        y: 6.5,
        w: 5,
        rotate: -11,
        line: {color: "ffffff", width: 1.5 },
      });
      
      slide.addText(
          [
              { text: year + "年", options: { fontFace: "Calibri", fontSize: 36, color: "ffffff", align: "right", breakLine: true } },
              { text: this.response.product_brand, options: { fontFace: "Calibri", fontSize: 36, color: "ffffff", align: "right", breakLine: true} },
              { text: "销售明细账分析", options: { fontFace: "Calibri", fontSize: 36, color: "ffffff", align: "right", } },
          ],
          { x: 3.5, y: 4.1, w: 8.5, h: 3.0, }
      );

    },
    color_header(table){
      list_header = []
      table.forEach((row,idx)=>{
        if (idx ==0){
          header = []
          for ( text of row){
            header.push({text,options: { fill: "2F5597", color: "ffffff", valign: "middle" }})
          }
          list_header.push(header)
        } else {
          list_header.push(row)
        }
      })
      return list_header
    },
    to_currency(a_list){
      new_list = []
      a_list.forEach((item,idx)=>{
        if(idx == 0){
          new_list.push(item)
        } else {
          new_list.push(item.toLocaleString('en-AU', { style: 'currency', currency: 'AUD' }))
        }
      })
      return new_list
    },
    genSlide02(pptx, year) {
      let slide = pptx.addSlide({ masterName: "MASTER_SLIDE" });
      slide.addText(year + "年总览", { x: 0.5, y: 0.6, w: 2.5, h: 0.4, align: "center", valign: "middle", color: "FFFFFF", fontFace: "Calibri",fontSize: 14  });  
      slide_one_table = this.color_header(this.response[year].total)
      slide_one_table[2] = this.to_currency(slide_one_table[2])    
      slide.addTable(slide_one_table, {
        x: 0.3,
        y: 1.5,
        rowH: [0.3, 0.5, 0.5],
        colW: [0.8, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 1],
        fill: { color: "F7F7F7" },
        color: "6c6c6c",
        fontSize: 11,
        valign: "center",
        align: "center",
        // border: { pt: "1", color: "BBCCDD" },
      }); 
      let opts = {
        x: 0.35,
        y: 3.3,
        w: 12.5,
        h: 3.5,
        barDir: "col",
        catAxisLabelColor: "666666",
        catAxisLabelFontFace: "Calibri",
        catAxisLabelFontSize: 16,
        catAxisOrientation: "minMax",
        showLegend: true,
        showTitle: false,
        legendPos: 't', 
        legendFontSize: 10,
        legendFontFace: "Calibri",
        // valAxisMaxVal: Auto,
        // valAxisMajorUnit: 10,

        valAxes: [
          {
            showValAxisTitle: true,
            valAxisTitle: "销售额(澳元)",
            valAxisTitleFontSize: 12,
            valAxisLabelFontFace: "Calibri",
          },
          {
            showValAxisTitle: true,
            valAxisTitle: "销售数量(个)",
            valAxisTitleFontSize: 12,
            valAxisLabelFontFace: "Calibri",
            valGridLine: { style: "none" },
          },
        ],
  
        catAxes: [
          {
            catAxisTitle: "Primary Category Axis",
          },
          {
            catAxisHidden: true,
          },
        ],
      };   
      let labels = this.response[year].total[0].slice(1,12);
      let chartTypes = [
        {
          type: pptx.charts.BAR,
          data: [
            {
              name: "销售金额",
              labels: labels,
              values: this.response[year].total[2].slice(1,12),
            },
          ],
          options: {
            chartColors: ["C55A11"],
            barGrouping: "stacked",
          },
        },
        {
          type: pptx.charts.LINE,
          data: [
            {
              name: "销售数量",
              labels: labels,
              values: this.response[year].total[1].slice(1,12),
            },
          ],
          options: {
            barGrouping: "standard",
            chartColors: ["2F5597"],
            lineSmooth: true,
            lineDataSymbol: 'none',
            secondaryValAxis: !!opts.valAxes,
            secondaryCatAxis: !!opts.catAxes,
          },
        },
      ];
      slide.addChart(chartTypes, opts);

    },
    slide_total_2_table(list_one,list_two){
      new_list = []
      list_two.forEach((row,idx)=>{
        if(idx < 6){
          new_list.push([row[0],list_one[idx][13],row[13].toLocaleString('en-AU', { style: 'currency', currency: 'AUD' })])
        } else {
          if(idx == 6){
            new_list.push(['其他',list_one[idx][13],row[13]])
          } else {
            new_list[6][1] = new_list[6][1] + list_one[idx][13]
            new_list[6][2] = new_list[6][2] + row[13]
            if(idx == list_two.length - 1){
              new_list[6][2]= new_list[6][2].toLocaleString('en-AU', { style: 'currency', currency: 'AUD' })
            }
          }
        }
      })
      return(new_list)
    },
    slide_total_2_table_2(list_one,list_two){
      new_list = []
      list_two.forEach((row,idx)=>{
        if(idx < 6){
          new_list.push([row[2],list_one[idx][15],row[15].toLocaleString('en-AU', { style: 'currency', currency: 'AUD' })])
        } else {
          if(idx == 6){
            new_list.push(['其他',list_one[idx][15],row[15]])
          } else {
            new_list[6][1] = new_list[6][1] + list_one[idx][15]
            new_list[6][2] = new_list[6][2] + row[15]
            if(idx == list_one.length - 1){
              new_list[6][2]= new_list[6][2].toLocaleString('en-AU', { style: 'currency', currency: 'AUD' })
            }
          }
        }
      })
      return(new_list)
    },


    genSlide03(pptx, year) {
      let slide = pptx.addSlide({ masterName: "MASTER_SLIDE" });
      slide.addText(year + "年总览分析", { x: 0.5, y: 0.6, w: 2.5, h: 0.4, align: "center", valign: "middle", color: "FFFFFF", fontFace: "Calibri",fontSize: 14  });  
     
      slide_total_2_table = this.color_header(this.slide_total_2_table(this.response[year].by_client_quantity,this.response[year].by_client_payment))
      slide_total_2_table_2 = this.color_header(this.slide_total_2_table_2(this.response[year].by_product_quantity,this.response[year].by_product_payment))

      slide.addText("TOP 5 销售渠道", { x: 0.3, y: 1.4, w: 2.5, h: 0.4, bold:true, align: "left", valign: "middle", color: "000000", fontFace: "Calibri",fontSize: 14  });  
      slide.addTable(slide_total_2_table, {
        x: 0.3,
        y: 1.8,
        rowH: [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3],
        colW: [3.9, 0.8, 1.2],
        fill: { color: "F7F7F7" },
        color: "6c6c6c",
        fontSize: 11,
        valign: "center",
        align: "center",
      }); 

      slide.addText("TOP 5 销售单品", { x: 0.3, y: 4.1, w: 2.5, h: 0.4, bold:true, align: "left", valign: "middle", color: "000000", fontFace: "Calibri",fontSize: 14  });  

      slide.addTable(slide_total_2_table_2, {
        x: 0.3,
        y: 4.5,
        rowH: [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3],
        colW: [3.9, 0.8, 1.2],
        fill: { color: "F7F7F7" },
        color: "6c6c6c",
        fontSize: 11,
        valign: "center",
        align: "center",
      }); 

      var barchart_label = []
      var barchart_quantity = []
      var barchart_payment = []
      slide_total_2_table.forEach((row,idx) => {
        if ( idx > 0 ) {
          barchart_label.push(row[0])
          barchart_quantity.push(row[1])
          barchart_payment.push(Number((row[2]).replace(/[^0-9.-]+/g,"")))
        }
      })
      var dchart_label = []
      var dchart_quantity = []
      var dchart_payment = []
      slide_total_2_table_2.forEach((row,idx) => {
        if ( idx > 0 ) {
          dchart_label.push(row[0])
          dchart_quantity.push(row[1])
          dchart_payment.push(Number((row[2]).toString().replace(/[^0-9.-]+/g,"")))
        }
      })



      let arrDataHighVals = [
        {
          labels: barchart_label,
          values: barchart_payment,
        },
      ];
      let dataChartPieStat = [
        {
          labels: dchart_label,
          values: dchart_payment,
        },
      ];

      let optsChartBar4 = {
        x: 6.7,
        y: 1.4,
        w: 6.0,
        h: 2.8,
        barDir: "col",
        barGapWidthPct: 60,
        chartColors: ["C55A11"],
        // chartColorsOpacity: 50,
        // valAxisMaxVal: 5000,
    
        catAxisLabelColor: "000000",
        catAxisLabelFontFace: "Calibri",
        catAxisLabelFontSize: 10,
        valAxisLabelFontFace: "Calibri",
        valAxisLabelFontSize: 10,
        // catAxisOrientation: "minMax",
    
        // dataBorder: { pt: "1", color: "F1F1F1" },
        // dataLabelColor: "ffffff",
        // dataLabelFontFace: "Calibri",
        // dataLabelFontSize: 10,
        // dataLabelPosition: "ctr",
        showTitle: true,
        titleColor: "000000",
        titleFontFace: "Calibri",
        titleFontSize: 12,
        title: year + "年TOP5渠道销售总金额",
        
    
        // showLegend: true,
        // legendPos: "t",
        // legendColor: "FF0000",
      };
      slide.addChart(pptx.charts.BAR, arrDataHighVals, optsChartBar4);

      let optsChartPie1 = {
        x: 6.7,
        y: 4.2,
        w: 6.0,
        h: 2.7,
        chartColors: ["c5117c", "c51122", "c55a11", "c5b411", "7cc511", "a6a6a6"],
        dataBorder: { pt: "2", color: "FFFFFF" },
        dataLabelColor: "FFFFFF",
        dataLabelFontFace: "Calibri",
        dataLabelFontSize: 12,
    
        legendPos: "r",
        legendFontFace: "Calibri",
        legendFontSize: 8,
    
        showLabel: false,
        showValue: false,
        showPercent: true,
        showLegend: true,
        showTitle: true,
    
        holeSize: 50,
    
        title: year + "年TOP5单品销售总金额占比",
        titleColor: "000000",
        titleFontFace: "Calibri",
        titleFontSize: 12,
      };
      slide.addChart(pptx.charts.DOUGHNUT, dataChartPieStat, optsChartPie1);

    },

    client_slide_table(list_one, client){
      var new_list = []
      list_one.forEach((row,idx)=>{
        if(idx < 11){
          new_list.push(row.slice(2,16).concat(row[16].toLocaleString('en-AU', { style: 'currency', currency: 'AUD' })))
          if(idx == list_one.length - 1){
              new_list[0][0] = client + ' TOP 10 销量单品'
          }  
        } else {
          if(idx == 11){
            new_list.push(['其他'].concat(row.slice(3,17)))
          } else {
            for (i of [2,3,4,5,6,7,8,9,10,11,12,13,14]){
              new_list[11][i] = new_list[11][i] + row[i+2]
            }
            if(idx == list_one.length - 1){
              new_list[0][0] = client + ' TOP 10 销量单品'
              new_list[11][14]= new_list[11][14].toLocaleString('en-AU', { style: 'currency', currency: 'AUD' })
            }
          }
        }
      })
      return(new_list)
    },

    client_slide_chart(list_one){
      var new_list = []
      list_one.forEach((row,idx)=>{
        if(idx < 4){
          new_list.push(row.slice(2,16).concat(row[16].toLocaleString('en-AU', { style: 'currency', currency: 'AUD' })))
        } else {
          if(idx == 4){
            new_list.push(['其他'].concat(row.slice(3,17)))
          } else {
            for (i of [2,3,4,5,6,7,8,9,10,11,12,13,14]){
              new_list[4][i] = new_list[4][i] + row[i+2]
            }
            if(idx == list_one.length - 1){
              new_list[4][14]= new_list[4][14].toLocaleString('en-AU', { style: 'currency', currency: 'AUD' })
            }
          }
        }
      })
      return(new_list)
    },

    genClientSlide(pptx, year, client){

      let slide = pptx.addSlide({ masterName: "MASTER_SLIDE" });
      slide.addText('渠道销量 - '+client, { x: 0.5, y: 0.6, w: 2.5, h: 0.4, align: "center", valign: "middle", color: "FFFFFF", fontFace: "Calibri",fontSize: 14  });  
      // slide.addText(client + " ", { x: 0.3, y: 1.4, w: 2.5, h: 0.4, bold:true, align: "left", valign: "middle", color: "000000", fontFace: "Calibri",fontSize: 14  });  
     


      var client_data = this.client_slide_table(this.response[year].pptx[client],client)
      var client_data_table = this.color_header(client_data)
      slide.addTable(client_data_table, {
        x: 0.3,
        y: 1.4,
        rowH: [0.2, 0.2, 0.2,0.2, 0.2,0.2, 0.2,0.2, 0.2,0.2, 0.2],
        colW: [3.9, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6,0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 1],
        fill: { color: "F7F7F7" },
        color: "6c6c6c",
        fontSize: 11,
        valign: "center",
        align: "center",
        // border: { pt: "1", color: "BBCCDD" },
      }); 

      var client_data_chart = this.client_slide_chart(this.response[year].pptx[client])
      // console.log(client_data_chart)


  
      let arrDataTimeline2ser = []
      let labels = client_data_chart[0].slice(1,13)
      client_data_chart.forEach((row,idx) => {
        let area = {}
        if ( idx > 0 ){
          area['name'] = row[0]
          area['labels'] = labels
          area['values'] = row.slice(1,13)
          arrDataTimeline2ser.push(area)
        }
       
      })
      arrDataTimeline2ser.reverse()

      // slide.addText("TOP 3 单品销量和总销量走势", { x: 0.3, y: 4.9, w: 4, h: 0.4, bold:true, align: "left", valign: "middle", color: "000000", fontFace: "Calibri",fontSize: 14  });  
      slide.addText(
          [
              { text: "TOP 3 单品", options: { bold:true, align: "left", valign: "middle", color: "000000", fontFace: "Calibri",fontSize: 14, breakLine: true } }, 
              { text: "和总销量走势", options: { bold:true, align: "left", valign: "middle", color: "000000", fontFace: "Calibri",fontSize: 14, } },
          ],
          {  x: 0.3, y: 4.9, w: 4, h: 0.4, }
      );
      if (arrDataTimeline2ser.length <4){
        var chartColor_list = ["117cc5","c55a11","c5117c"]
      } else {
        var chartColor_list = ["a6a6a6","117cc5","c55a11","c5117c"]
      }
      let optsChartLine2 = {
        x: 0.3,
        y: 4.7,
        w: "95%",
        h: 2.5,
        
        chartColors: chartColor_list,
        chartColorsOpacity: 80,
        // valAxisLabelRotate: 5,
        dataBorder: { pt: 1, color: "FFFFFF" },
        showValue: false,
        showLegend: true,
        legendPos: 'l',
        catAxisLabelFontFace: "Calibri",
        valAxisLabelFontFace: "Calibri",
        legendFontFace:"Calibri",


        // fill: "D1E1F1",

        barGrouping: "stacked",
      };
      slide.addChart(pptx.charts.AREA, arrDataTimeline2ser, optsChartLine2);



    },

    genSlideMiddle(pptx, year) {
      let slide = pptx.addSlide({ masterName: "TITLE_SLIDE" });
  
      slide.addShape(pptx.shapes.RIGHT_TRIANGLE, {
        x: -1,
        y: -1,
        w: 6.2,
        h: 6.2,
        rotate: 90,
        line: { color: '333f50', width: 1.5 },
      });
      slide.addShape(pptx.shapes.RIGHT_TRIANGLE, {
        x: 0,
        y: 0,
        w: 3.5,
        h: 3.5,
        rotate: 90,
        fill: { color: 'A6A6A6' },
      });
      slide.addShape(pptx.shapes.RIGHT_TRIANGLE, {
        x: 5,
        y: 4.3,
        w: 8,
        h: 3,
        // rotate: 270,
        flipH: true,
        fill: { color: '333f50' },
      });

      slide.addShape(pptx.shapes.LINE, {
        x: 7.2,
        y: 6.5,
        w: 5,
        rotate: -11,
        line: {color: "ffffff", width: 1.5 },
      });
      
      slide.addText(
          [
              { text: this.response.product_brand, options: { fontFace: "Calibri", fontSize: 36, color: "000000", align: "center", breakLine: true} },
              { text: year + "年各渠道销量分析", options: { fontFace: "Calibri", fontSize: 36, color: "000000", align: "center", breakLine: true } },
              { text: "(渠道排序根据总销量由高至低)", options: { fontFace: "Calibri", fontSize: 18, color: "000000", align: "center", } },
          ],
          { x: 0, y: 2.2, w: "100%", h: 3.0, }
      );

    },
    genSlideEnd(pptx, year) {
      let slide = pptx.addSlide({ masterName: "TITLE_SLIDE" });
  
      slide.addShape(pptx.shapes.RIGHT_TRIANGLE, {
        x: -1,
        y: -1,
        w: 6.2,
        h: 6.2,
        rotate: 90,
        line: { color: '333f50', width: 1.5 },
      });
      slide.addShape(pptx.shapes.RIGHT_TRIANGLE, {
        x: 0,
        y: 0,
        w: 3.5,
        h: 3.5,
        rotate: 90,
        fill: { color: 'A6A6A6' },
      });
      slide.addShape(pptx.shapes.RIGHT_TRIANGLE, {
        x: 5,
        y: 4.3,
        w: 8,
        h: 3,
        // rotate: 270,
        flipH: true,
        fill: { color: '333f50' },
      });

      slide.addShape(pptx.shapes.LINE, {
        x: 7.2,
        y: 6.5,
        w: 5,
        rotate: -11,
        line: {color: "ffffff", width: 1.5 },
      });
      
      slide.addText(
          [
              { text: '感谢阅读', options: { fontFace: "Calibri", fontSize: 36, color: "000000", align: "center", breakLine: true} },
          ],
          { x: 0, y: 2.2, w: "100%", h: 3.0, }
      );

    },
   

    
}

})