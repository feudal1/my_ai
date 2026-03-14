using System;
using SolidWorks.Interop.sldworks;
using SolidWorks.Interop.swconst;
using tools;
using cad_tools;

namespace tools
{
    partial class Program
    {
        [Command("export", Description = "导出当前零件展开为 DWG 文件", Parameters = "无", Group = "solidworks")]
        static void ExportCommand(string[] args)
        {
            if (swApp == null || swModel == null) return;

            var thickness = get_thickness.run(swModel);
            var dwgname = Exportdwg.run(swModel, thickness.ToString());
      
        }

        [Command("export_flat_view", Description = "导出钣金展开视图 dwg", Parameters = "无", Group = "solidworks")]
        static void ExportFlatViewCommand(string[] args)
        {
            if (swApp == null || swModel == null) return;
        
            var thickness = get_thickness.run(swModel);
            Exportdwg.run(swModel, thickness.ToString());
        }


        [Command("asm2export", Description = "装配体批量导出 dwg", Parameters = "无", Group = "solidworks")]
        static void Asm2Export2Command(string[] args)
        {
            if (swApp == null || swModel == null) return;

            asm2export.run(swApp, swModel);
        }


        [Command("asm2drw", Description = "装配体批量生成工程图", Parameters = "无", Group = "solidworks")]
        static void Asm2DrwCommand(string[] args)
        {
            if (swApp == null || swModel == null) return;

            string[]? partnames = Getallpartname.run(swModel);
            if (partnames != null && partnames.Length > 0)
            {
                foreach (var partname in partnames)
                {
                    Profiler.Time(() => open_part_by_name.run(swApp, partname));
                    var thickness = Profiler.Time(() => get_thickness.run(swModel));
                    Profiler.Time(() => New_drw.run(swApp, swModel));
                    Profiler.Time(() => close_current_doc.run(swApp, swModel));
                }
            }
        }

        [Command("unsuppress", Description = "解除压缩特征或零部件", Parameters = "无", Group = "solidworks")]
        static void UnsuppressCommand(string[] args)
        {
            if (swModel == null) return;

            Unsupress.run(swModel);
        }

        [Command("get_select_part_name", Description = "获取选中零件的名称", Parameters = "需先选择零件", Group = "solidworks")]
        static void GetSelectPartNameCommand(string[] args)
        {
            if (swModel == null) return;

            Getselectpartname.run(swModel);
        }

        [Command("get_all_part_name", Description = "获取装配体中所有零件名称", Parameters = "无", Group = "solidworks")]
        static void GetAllPartNameCommand(string[] args)
        {
            if (swModel == null) return;

            Getallpartname.run(swModel);
        }

        [Command("open_part_by_name", Description = "按名称打开零件", Parameters = "<零件名称>", Group = "solidworks")]
        static void OpenPartByNameCommand(string[] args)
        {
            if (swApp == null) return;

            if (args.Length > 1)
            {
                open_part_by_name.run(swApp, args[1]);
            }
            else
            {
                Console.WriteLine("请提供零件名称参数");
            }
        }

        [Command("new_drw", Description = "新建工程图", Parameters = "无", Group = "solidworks")]
        static void NewDrwCommand(string[] args)
        {
            if (swApp == null || swModel == null) return;
            add_name2info.run(swModel);
            New_drw.run(swApp, swModel);
        }

        [Command("get_current_doc_name", Description = "获取当前文档名称", Parameters = "无", Group = "solidworks")]
        static void GetCurrentDocNameCommand(string[] args)
        {
            if (swModel == null) return;

            Getcurrentdocname.run(swModel);
        }

        [Command("close_current_doc", Description = "关闭当前文档", Parameters = "无", Group = "solidworks")]
        static void CloseCurrentDocCommand(string[] args)
        {
            if (swApp == null || swModel == null) return;

            close_current_doc.run(swApp, swModel);
        }

        [Command("get_thickness", Description = "获取零件厚度", Parameters = "无", Group = "solidworks")]
        static void GetThicknessCommand(string[] args)
        {
            if (swModel == null) return;

            get_thickness.run(swModel);
        }

        [Command("get_thickness_from_solidfolder", Description = "从实体文件夹获取厚度", Parameters = "无", Group = "solidworks")]
        static void GetThicknessFromSolidFolderCommand(string[] args)
        {
            if (swModel == null) return;

            get_thickness_from_solidfolder.run(swModel);
        }

        [Command("open_doc_folder", Description = "打开零件所在文件夹", Parameters = "无", Group = "solidworks")]
        static void OpenDocFolderCommand(string[] args)
        {
            if (swModel == null) return;

            open_doc_folder.run(swModel);
        }

        [Command("plan1", Description = "综合计划：添加名称 + 获取厚度 + 导出 dwg + 生成工程图", Parameters = "无", Group = "solidworks")]
        static void Plan1Command(string[] args)
        {
            if (swApp == null || swModel == null) return;

            add_name2info.run(swModel);
            var thickness = get_thickness.run(swModel);
            NativeClipboard.SetText(thickness.ToString() + "厘");
            var dwgname = Exportdwg.run(swModel, thickness.ToString());
            New_drw.run(swApp, swModel);
        }

        [Command("get_dim_info", Description = "【AI 训练使用】获取尺寸标注信息", Parameters = "无", Group = "solidworks")]
        static void GetDimInfoCommand(string[] args)
        {
            if (swModel == null) return;

            get_dim_info.run(swModel);
        }

        [Command("get_views_graph", Description = "【AI 训练使用】获取视图图形结构", Parameters = "无", Group = "solidworks")]
        static void GetViewsGraphCommand(string[] args)
        {
            if (swApp == null || swModel == null) return;

            get_views_graph.run(swModel);
        }

        [Command("get_all_face", Description = "【AI 训练使用】获取所有面信息", Parameters = "无", Group = "solidworks")]
        static void GetAllFaceCommand(string[] args)
        {
            if (swModel == null) return;

            get_all_face.run(swModel);
        }

        [Command("get_all_edges", Description = "【AI 训练使用】获取所有边信息", Parameters = "无", Group = "solidworks")]
        static void GetAllEdgesCommand(string[] args)
        {
            if (swModel == null) return;

            get_all_edges.run(swModel);
        }

        [Command("export2", Description = "导出当前零件展开为 DWG 文件（版本 2）", Parameters = "无", Group = "solidworks")]
        static void Export2Command(string[] args)
        {
            if (swApp == null || swModel == null) return;

             var thickness = get_thickness.run(swModel);
            exportdwg2.run(swModel, thickness.ToString());
        }
             [Command("drw2dwg", Description = "将工程图转换为 DWG 格式", Parameters = "无", Group = "solidworks")]
        static void Drw2DwgCommand(string[] args)
        {
            if (swApp == null || swModel == null) return;

            var dwgFileName =drw2dwg.run(swModel, swApp);
            open_cad_doc_by_name.run(dwgFileName);
        }
                [Command("add_name2info", Description = "添加零件名称到自定义属性", Parameters = "无", Group = "solidworks")]
        static void AddName2InfoCommand(string[] args)
        {
            if (swModel == null) return;

            add_name2info.run(swModel);
        }
    }
}

