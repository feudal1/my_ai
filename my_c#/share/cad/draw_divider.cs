using Autodesk.AutoCAD.Interop;
using Autodesk.AutoCAD.Interop.Common;
using System;

namespace cad_tools
{
    public class draw_divider
    {
        /// <summary>
        /// 在当前 DWG 文件中绘制一个矩形框，用于框选某个区域的 DWG 文件
        /// </summary>
        /// <param name="minX">框的左下角 X 坐标</param>
        /// <param name="minY">框的左下角 Y 坐标</param>
        /// <param name="maxX">框的右上角 X 坐标</param>
        /// <param name="maxY">框的右上角 Y 坐标</param>
        static public void run(double minX = 0.0, double minY = 0.0, double maxX = 1000.0, double maxY = 1000.0)
        {
            AcadApplication? acadApp = CadConnect.GetOrCreateInstance();
            if (acadApp == null)
            {
                Console.WriteLine("错误：无法连接到 AutoCAD 应用程序。");
                return;
            }

            AcadDocument? acadDoc = acadApp.ActiveDocument;
            if (acadDoc == null)
            {
                Console.WriteLine("错误：没有活动的 AutoCAD 文档。");
                return;
            }

            try
            {
                // 创建轻量多段线作为矩形框
                var polyline = (AcadLWPolyline)acadDoc.ModelSpace.AddLightWeightPolyline(
                    new double[] { 
                        minX, minY,
                        maxX, minY,
                        maxX, maxY,
                        minX, maxY,
                        minX, minY  // 闭合
                    }
                );
                polyline.Closed = true;
                polyline.color = ACAD_COLOR.acYellow; // 黄色框
      
                polyline.Layer = "BOUNDARY"; // 放到边界层
                
                Console.WriteLine($"成功绘制边界框：({minX:F2}, {minY:F2}) 到 ({maxX:F2}, {maxY:F2})");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"绘制边界框失败：{ex.Message}");
                if (ex.InnerException != null)
                    Console.WriteLine($"内部异常：{ex.InnerException.Message}");
            }
        }

        /// <summary>
        /// 处理子文件夹遍历并为每个子文件夹的 DWG 文件绘制边界框（支持有子文件夹和没有子文件夹两种情况）
        /// </summary>
        static public void process_subfolders_with_divider()
        {
            string? selectedFolder = FolderPicker.SelectFolder();
            if (string.IsNullOrEmpty(selectedFolder))
            {
                Console.WriteLine("未选择文件夹，操作取消。");
                return;
            }
           
            double boxHalfHeight = 600.0; // Y 方向半高（±600）
            double yOffsetPerFolder = 1200.0; // 每个文件夹的 Y 偏移增量
            
            // 获取所有子文件夹
            var subDirectories = Directory.GetDirectories(selectedFolder);
            
            int folderIndex = 0;
            
            // 情况 1：如果有子文件夹，遍历子文件夹
            if (subDirectories.Length > 0)
            {
                foreach (var subDir in subDirectories)
                {
                    Console.WriteLine($"\n处理子文件夹：{Path.GetFileName(subDir)}");
                    
                    // 计算当前文件夹的 Y 偏移
                    double currentYOffset = folderIndex * yOffsetPerFolder;
                    
                    // 获取子文件夹中的所有 DWG 文件
                    var dwgFiles = Directory.GetFiles(subDir, "*.dwg");
                    
                    if (dwgFiles.Length > 0)
                    {
                        AcadApplication? acadApp = CadConnect.GetOrCreateInstance();
                        
                        if (acadApp != null && acadApp.ActiveDocument != null)
                        {
                            // 设置 Y 方向的范围：基于当前文件夹的 Y 偏移 ±600
                            double boxMinY = currentYOffset - boxHalfHeight;
                            double boxMaxY = currentYOffset + boxHalfHeight;
                            
                            // X 从 0 开始（不要偏移）
                            double frameStartX = 0.0;
                            
                            Console.WriteLine($"开始合并子文件夹 {Path.GetFileName(subDir)} 的 {dwgFiles.Length} 个文件，Y 偏移={currentYOffset:F2}");
                            
                            // 合并该子文件夹的所有 DWG，每个文件按序号递增 X 偏移
                            for (int i = 0; i < dwgFiles.Length; i++)
                            {
                                merge_dwg.run(dwgFiles[i], currentYOffset, i);
                            }
                            
                            // 计算边界框的最大 X 值：最后一个文件的 X 位置 + 固定宽度
                            double boxMaxX = (dwgFiles.Length - 1) * 1000.0 + 500.0 + 600.0;
                            
                            // 确保框的宽度至少为 100
                            if (boxMaxX < 100)
                            {
                                boxMaxX = 100;
                            }
                            
                            // 现在绘制完整的边界框，从 X=0 开始
                            run(frameStartX, boxMinY, boxMaxX, boxMaxY);
                            
                            Console.WriteLine($"已绘制子文件夹 {Path.GetFileName(subDir)} 的边界框：X({frameStartX:F2} 到 {boxMaxX:F2}), Y({boxMinY:F2} 到 {boxMaxY:F2})");
                        }
                        else
                        {
                            Console.WriteLine($"警告：无法获取 AutoCAD 文档，跳过边界框绘制");
                        }
                    }
                    else
                    {
                        Console.WriteLine($"子文件夹 {Path.GetFileName(subDir)} 中没有 DWG 文件");
                    }
                    
                    folderIndex++;
                }
            }
            // 情况 2：如果没有子文件夹，直接处理当前文件夹中的 DWG 文件
            else
            {
                Console.WriteLine($"\n未找到子文件夹，直接处理当前文件夹：{Path.GetFileName(selectedFolder)}");
                
                // 获取当前文件夹中的所有 DWG 文件
                var dwgFiles = Directory.GetFiles(selectedFolder, "*.dwg");
                
                if (dwgFiles.Length > 0)
                {
                    AcadApplication? acadApp = CadConnect.GetOrCreateInstance();
                    
                    if (acadApp != null && acadApp.ActiveDocument != null)
                    {
                        // Y 方向从 0 开始
                        double currentYOffset = 0.0;
                        double boxMinY = currentYOffset - boxHalfHeight;
                        double boxMaxY = currentYOffset + boxHalfHeight;
                        
                        // X 从 0 开始
                        double frameStartX = 0.0;
                        
                        Console.WriteLine($"开始合并当前文件夹的 {dwgFiles.Length} 个文件");
                        
                        // 合并所有 DWG，每个文件按序号递增 X 偏移
                        for (int i = 0; i < dwgFiles.Length; i++)
                        {
                            merge_dwg.run(dwgFiles[i], currentYOffset, i);
                        }
                        
                        // 计算边界框的最大 X 值
                        double boxMaxX = (dwgFiles.Length - 1) * 1000.0 + 500.0 + 600.0;
                        
                        // 确保框的宽度至少为 100
                        if (boxMaxX < 100)
                        {
                            boxMaxX = 100;
                        }
                        
                        // 绘制边界框，从 X=0 开始
                        run(frameStartX, boxMinY, boxMaxX, boxMaxY);
                        
                        Console.WriteLine($"已绘制当前文件夹的边界框：X({frameStartX:F2} 到 {boxMaxX:F2}), Y({boxMinY:F2} 到 {boxMaxY:F2})");
                    }
                    else
                    {
                        Console.WriteLine($"警告：无法获取 AutoCAD 文档，跳过边界框绘制");
                    }
                }
                else
                {
                    Console.WriteLine($"当前文件夹中没有 DWG 文件");
                }
            }
            
            Console.WriteLine("\n所有处理完成！");
        }

       
    }
}